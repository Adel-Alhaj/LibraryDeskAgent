from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.models import Book, Order, OrderItem, Customer

async def find_books(db: AsyncSession, q: str, by: str = "title") -> list[dict]:
    """Find books by title or author."""
    query = select(Book) # Start with: SELECT * FROM books
    if by == "title":
        query = query.where(Book.title.ilike(f"%{q}%")) # ilike  case-insensitive LIKE
    elif by == "author":
        query = query.where(Book.author.ilike(f"%{q}%")) # f"%{q}%" matches anywhere in the string
    else:
        raise ValueError("by parameter must be 'title' or 'author'")
    
    result = await db.execute(query)
    books = result.scalars().all()
    return [
        {
            "isbn": b.isbn, 
            "title": b.title, 
            "author": b.author, 
            "stock": b.stock, 
            "price": float(b.price)
        } for b in books
    ]

async def create_order(db: AsyncSession, customer_id: int, items: list[dict]) -> int:
    """Create a new order and reduce stock."""
    # Verify customer exists
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise ValueError(f"Customer {customer_id} not found")
    
    order = Order(customer_id=customer_id, status="pending")
    db.add(order)
    await db.flush()
    
    for item in items:
        book = await db.get(Book, item["isbn"])
        if not book:
            await db.rollback()
            raise ValueError(f"Book {item['isbn']} not found")
        if book.stock < item["qty"]:
            await db.rollback()
            raise ValueError(f"Not enough stock for {book.title}. Available: {book.stock}, Requested: {item['qty']}")
        
        book.stock -= item["qty"]
        order_item = OrderItem(
            order_id=order.id, 
            isbn=item["isbn"], 
            qty=item["qty"],
            price=book.price
        )
        db.add(order_item)
    
    await db.commit()
    return order.id

async def restock_book(db: AsyncSession, isbn: str, qty: int) -> dict:
    """Increase stock of a book."""
    book = await db.get(Book, isbn)
    if not book:
        raise ValueError(f"Book {isbn} not found")
    
    old_stock = book.stock
    book.stock += qty
    await db.commit()
    
    return {
        "isbn": isbn,
        "title": book.title,
        "old_stock": old_stock,
        "new_stock": book.stock,
        "added": qty
    }

async def update_price(db: AsyncSession, isbn: str, price: float) -> dict:
    """Update the price of a book."""
    book = await db.get(Book, isbn)
    if not book:
        raise ValueError(f"Book {isbn} not found")
    
    old_price = book.price
    book.price = price
    await db.commit()
    
    return {
        "isbn": isbn,
        "title": book.title,
        "old_price": float(old_price),
        "new_price": float(price)
    }

async def order_status(db: AsyncSession, order_id: int) -> dict:
    """Get order status with details."""
    order = await db.get(Order, order_id)
    if not order:
        return {"error": "Order not found"}
    
    # Get order items
    result = await db.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    items = result.scalars().all()
    
    return {
        "order_id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": [
            {
                "isbn": item.isbn,
                "qty": item.qty,
                "price": float(item.price) if item.price else None
            } for item in items
        ]
    }

async def inventory_summary(db: AsyncSession, low_stock_threshold: int = 3) -> list[dict]:
    """Get stock summary of all books, highlighting low stock items."""
    result = await db.execute(
        select(Book)
        .where(Book.stock <= low_stock_threshold)  # FILTER
        .order_by(Book.stock.asc())
    )
    books = result.scalars().all()
    
    return [
        {
            "isbn": b.isbn,
            "title": b.title,
            "author": b.author,
            "stock": b.stock,
            "price": float(b.price),
            "low_stock": True  # Now always True since we filtered
        } for b in books
    ]