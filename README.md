# Library Desk Agent

An AI-powered chat interface for managing library operations including book inventory, customer orders, and stock management.

## Features

- **Book Search**: Find books by title or author
- **Order Management**: Create orders and automatically adjust inventory
- **Inventory Control**: Restock books and update prices
- **Order Tracking**: Check order status and details
- **Inventory Reports**: View stock summaries and low-stock alerts
- **Conversational AI**: Natural language processing with context-aware responses

## Tech Stack

**Backend:**
- FastAPI
- SQLAlchemy (async)
- SQLite
- LangChain
- OpenAI GPT-4

**Frontend:**
- Pure HTML/CSS/JavaScript (no frameworks)
- Clean black and white design

## Project Structure
```
LibraryDeskAgent/
├── app/                  # Frontend application
│   └── index.html        # Main entry point for the UI
├── server/               # Backend logic (FastAPI)
│   ├── agent.py          # AI Agent logic and decision making
│   ├── config.py         # Configuration and environment variables loader
│   ├── db.py             # Database connection and session management
│   ├── main.py           # FastAPI application entry point
│   ├── models.py         # SQLAlchemy/Database models
│   ├── schemas.py        # Pydantic models for data validation
│   ├── seed.py           # Script to populate the database with initial data
│   └── tools.py          # Agent tools
├── .env                  # Environment variables (secret)
├── .env.example          # Template for environment variables
├── .gitignore            # Files and folders to be ignored by Git
├── library.db            # Local SQLite database file
├── README.md             # Project documentation
└── requirements.txt      # List of Python dependencies
```

## Installation

### Prerequisites

- Python 3.10+
- OpenAI API key

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Adel-Alhaj/LibraryDeskAgent
cd LibraryDeskAgent
```

2. **Create virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```
   
Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. **Initialize database**
```bash
python server/seed.py
```

## Running the Application

### Start Backend Server
```bash
uvicorn server.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

**To view API documentation:** Open `http://localhost:8000/docs` in your browser

**To stop the server:** Press `Ctrl+C` in the terminal

### Start Frontend

Simply open `app/index.html` directly in your web browser (double-click the file)

## Usage Examples

Try these queries in the chat interface:

### Search Books
```
Find books by Martin Fowler
Show me books with "Clean" in the title
```

### Create Orders
```
Create an order for customer 1 with 2 copies of '9780132350884'
We sold 3 copies of Clean Code to customer 2 today
```

### Inventory Management
```
Restock The Pragmatic Programmer by 10
Update the price of '9780132350884' to 45.99
Show me the inventory summary
```

### Order Status
```
What's the status of order 1?
Show me details for order 3
```

### Multi-step Operations
```
Restock The Pragmatic Programmer by 10 and list all books by Andrew Hunt
```

## API Endpoints

### POST `/chat`
Main chat endpoint for interacting with the agent.

**Request:**
```json
{
  "session_id": "session_123",
  "message": "Find books by Martin Fowler"
}
```

**Response:**
```json
{
  "session_id": "session_123",
  "reply": "I found the following books by Martin Fowler: ..."
}
```

### GET `/`
Health check endpoint.

### GET `/docs`
Interactive API documentation (Swagger UI).

## Database Schema

### Tables

**books**
- `isbn` (PK): Book ISBN
- `title`: Book title
- `author`: Author name
- `stock`: Current inventory count
- `price`: Book price

**customers**
- `id` (PK): Customer ID
- `name`: Customer name
- `email`: Customer email

**orders**
- `id` (PK): Order ID
- `customer_id` (FK): Reference to customers
- `status`: Order status
- `created_at`: Order creation timestamp

**order_items**
- `id` (PK): Order item ID
- `order_id` (FK): Reference to orders
- `isbn` (FK): Reference to books
- `qty`: Quantity ordered
- `price`: Price at time of order

**messages**
- `id` (PK): Message ID
- `session_id`: Chat session identifier
- `role`: 'user' or 'assistant'
- `content`: Message text
- `created_at`: Message timestamp

**tool_calls**
- `id` (PK): Tool call ID
- `session_id`: Chat session identifier
- `name`: Tool name
- `args_json`: Tool arguments (JSON)
- `result_json`: Tool result (JSON)
- `created_at`: Execution timestamp

## Seed Data

The database is pre-seeded with:
- **10 books** from various technical authors
- **6 customers** with contact information
- **4 sample orders** with order items

## Development

### Adding New Tools

1. Create the function in `server/tools.py`:
```python
async def my_new_tool(db: AsyncSession, param: str) -> dict:
    # Implementation
    pass
```

2. Wrap it in `server/agent.py`:
```python
@tool
async def my_new_tool_tool(param: str) -> dict:
    """Tool description for the LLM."""
    return await my_new_tool(db=db, param=param)
```

3. Add to the tools list in `run_agent()`

### Customizing the UI

Edit `app/index.html`:
- Modify CSS in `<style>` section for appearance
- Update JavaScript for different behavior
- Change suggestions in the welcome message

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is available
- Verify OpenAI API key is set in `.env`
- Ensure all dependencies are installed with `pip install -r requirements.txt`
- Make sure virtual environment is activated

**Frontend can't connect:**
- Confirm backend is running on port 8000
- Check browser console for CORS errors (F12 → Console tab)
- Verify API_URL in `index.html` is set to `http://localhost:8000`

**Database errors:**
- Delete `library.db` and re-run `python server/seed.py`
- Check SQLite is properly installed
- Verify database schema matches models

**Agent not responding correctly:**
- Check OpenAI API key is valid and has credits
- Review agent logs in terminal (verbose=True shows detailed execution)
- Verify tool definitions match expected schemas
- If agent hallucinates ISBNs, check that system prompt instructs it to search for books first

**Agent hallucinating book ISBNs:**
- The agent must use `find_books` tool first before using any ISBN
- Check system prompt includes instructions to look up books by title first
- Never let the agent guess ISBN numbers

## Notes

- Session data persists in the database
- Each browser session generates a unique session_id
- Tool calls are logged for debugging and auditing
- The agent maintains conversation context within sessions
- API documentation is automatically generated at `/docs` endpoint