from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from typing import List
import json
from datetime import datetime

from server.tools import (
    find_books,
    create_order,
    restock_book,
    update_price,
    order_status,
    inventory_summary
)
from server.models import Message, ToolCall
from server.schemas import CreateOrderInput

# -------------------------
# GPT LLM
# -------------------------
# LangChain automatically read the api key from the environment
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0
)

# -------------------------
# Run agent
# -------------------------
# CLOSURE: db and session_id are injected here, tools defined inside have no db, sessions_id params - LLM only sees business data (abstraction)
async def run_agent(session_id: str, user_message: str, db: AsyncSession) -> str:
    
    # Load chat history for context
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .limit(20)
    )

    # .scalars().all() - Extracts the actual Message objects, then return all results as a list
    previous_messages = result.scalars().all()
    
    # Convert previous_messages to Langchain format
    chat_history = []
    for msg in previous_messages:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            chat_history.append(AIMessage(content=msg.content))
    


    # Save user message to database
    user_msg = Message(session_id=session_id, role="user", content=user_message)
    db.add(user_msg)
    await db.commit()

    # Tools are defined internally to handle session_id and db session injection
    # @tool decorator sends JSON to the llm contains the description of the tool
    @tool
    async def find_books_tool(q: str, by: str = "title") -> list[dict]:
        """Find books by title or author. Use 'by' parameter to specify search field ('title' or 'author')."""
        result = await find_books(db=db, q=q, by=by)
        
        # Log tool call in db
        tool_call = ToolCall(
            session_id=session_id,
            name="find_books",
            args_json=json.dumps({"q": q, "by": by}),
            result_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(tool_call)
        await db.commit()
        
        return result

    @tool(args_schema=CreateOrderInput) # The structure of the tool input must follow this schema
    async def create_order_tool(customer_id: int, items: List[dict]) -> dict:
        """
        Create a new order for a customer and reduce stock accordingly.
        
        Args:
            customer_id: The ID of the customer placing the order
            items: List of items, each containing 'isbn' (book ISBN) and 'qty' (quantity)
                   Example: [{"isbn": "9780132350884", "qty": 2}, {"isbn": "9780201616224", "qty": 1}]
        
        Returns:
            Dictionary with order_id and confirmation message
        """
        # Convert Pydantic models to dicts if needed
        items_list = []
        for item in items:
            if isinstance(item, dict):
                items_list.append(item)
            else:
                items_list.append({"isbn": item.isbn, "qty": item.qty})
        
        order_id = await create_order(db=db, customer_id=customer_id, items=items_list)
        result = {
            "order_id": order_id, 
            "message": f"Order {order_id} created successfully for customer {customer_id}",
            "items_count": len(items_list)
        }
        
        # Log tool call
        tool_call = ToolCall(
            session_id=session_id,
            name="create_order",
            args_json=json.dumps({"customer_id": customer_id, "items": items_list}),
            result_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(tool_call)
        await db.commit()
        
        return result

    @tool
    async def restock_book_tool(isbn: str, qty: int) -> dict:
        """Increase stock of a book by the specified quantity."""
        await restock_book(db=db, isbn=isbn, qty=qty)
        result = {"message": f"Successfully restocked {isbn} by {qty} units"}
        
        # Log tool call
        tool_call = ToolCall(
            session_id=session_id,
            name="restock_book",
            args_json=json.dumps({"isbn": isbn, "qty": qty}),
            result_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(tool_call)
        await db.commit()
        
        return result

    @tool
    async def update_price_tool(isbn: str, price: float) -> dict:
        """Update the price of a book."""
        await update_price(db=db, isbn=isbn, price=price)
        result = {"message": f"Successfully updated price for {isbn} to ${price}"}
        
        # Log tool call
        tool_call = ToolCall(
            session_id=session_id,
            name="update_price",
            args_json=json.dumps({"isbn": isbn, "price": price}),
            result_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(tool_call)
        await db.commit()
        
        return result

    @tool
    async def order_status_tool(order_id: int) -> dict:
        """Get the status of an order by order ID."""
        status = await order_status(db=db, order_id=order_id)
        result = status
        
        # Log tool call
        tool_call = ToolCall(
            session_id=session_id,
            name="order_status",
            args_json=json.dumps({"order_id": order_id}),
            result_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(tool_call)
        await db.commit()
        
        return result

    @tool
    async def inventory_summary_tool() -> list[dict]:
        """Get inventory summary showing all books and their current stock levels."""
        result = await inventory_summary(db=db)
        
        # Log tool call
        tool_call = ToolCall(
            session_id=session_id,
            name="inventory_summary",
            args_json=json.dumps({}),
            result_json=json.dumps(result),
            created_at=datetime.utcnow()
        )
        db.add(tool_call)
        await db.commit()
        
        return result
    
    # Langchain converts each tool into a JSON schema has description of each tool
    # This JSON schema is sent to the llm with every request
    tools = [
        find_books_tool,
        create_order_tool,
        restock_book_tool,
        update_price_tool,
        order_status_tool,
        inventory_summary_tool
    ]

    # -------------------------
    # Prompt with proper placeholders
    # -------------------------
    prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful library desk agent assistant. You can help with:
- Finding books by title or author
- Creating orders for customers (specify customer_id and list of items with isbn and qty)
- Restocking books
- Updating book prices
- Checking order status
- Getting inventory summaries

CRITICAL RULES:
1. When a user mentions a book by TITLE (e.g., "Clean Code", "The Pragmatic Programmer"), you MUST:
   - First call find_books tool to get the correct ISBN
   - Then use that ISBN for any operations (restock, update price, create order)
   - NEVER make up or guess ISBN numbers

2. Only use ISBN numbers that you have retrieved from find_books tool or that the user explicitly provides

3. If the user says "restock Clean Code", your workflow should be:
   - Step 1: Call find_books with q="Clean Code" and by="title"
   - Step 2: Use the ISBN from the result to call restock_book

Use the available tools to complete user requests accurately. When multiple actions are requested, execute them in sequence.

When creating orders:
- Each item needs an ISBN (the book identifier) and quantity
- Format: customer_id with items as list of isbn and qty pairs
- Example: customer 1 ordering 2 copies of book X and 1 copy of book Y"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    # chat_history: long term memory (previous messages)
    # chat_history: filled manually in ainvoke()

    # agent_scratchpad: working memory (current called tools) (used when calling more than 1 tool for the same response)
    # agent_scratchpad: filled automatically by langchain
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        #verbose=True, # Prints the agent's thought process (debugging)
        handle_parsing_errors=True,
        max_iterations=10 # Prevent infinite loops (max 10 tool calls)
    )

    try:
        # Execute the agent with chat history
        result = await executor.ainvoke({
            "input": user_message,
            "chat_history": chat_history  # This fills the chat_history placeholder
        })

        # Save assistant response to database
        assistant_msg = Message(
            session_id=session_id, 
            role="assistant", 
            content=result["output"]
        )
        db.add(assistant_msg)
        await db.commit()

        print("Agent response:- \n", result["output"])
        return result["output"]
    
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        # Save error message
        assistant_msg = Message(
            session_id=session_id, 
            role="assistant", 
            content=error_msg
        )
        db.add(assistant_msg)
        await db.commit()
        return error_msg