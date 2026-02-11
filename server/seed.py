import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base, Book, Customer, Order, OrderItem
from sqlalchemy import text

# Create database engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def seed_database():
    """Seed the database with initial data."""
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Add seed data
    async with AsyncSessionLocal() as session: # Automatically manages the session lifecycle (open, close)
        
        # Add 10 books
        books = [
            Book(isbn="9780132350884", title="Clean Code", author="Robert C. Martin", stock=10, price=35.99),
            Book(isbn="9780201616224", title="The Pragmatic Programmer", author="Andrew Hunt", stock=5, price=42.99),
            Book(isbn="9781491954248", title="Designing Data-Intensive Applications", author="Martin Kleppmann", stock=8, price=45.99),
            Book(isbn="9780134757599", title="The Mythical Man-Month", author="Frederick Brooks", stock=3, price=29.99),
            Book(isbn="9780321125217", title="Domain-Driven Design", author="Eric Evans", stock=4, price=55.99),
            Book(isbn="9780596007126", title="Head First Design Patterns", author="Eric Freeman", stock=6, price=49.99),
            Book(isbn="9780131101633", title="The C Programming Language", author="Brian Kernighan", stock=2, price=39.99),
            Book(isbn="9780131177055", title="Refactoring", author="Martin Fowler", stock=7, price=37.99),
            Book(isbn="9780321146533", title="Test-Driven Development", author="Kent Beck", stock=4, price=32.99),
            Book(isbn="9780137081073", title="Effective Java", author="Joshua Bloch", stock=5, price=48.99),
        ]
        session.add_all(books)
        
        # Add 6 customers
        customers = [
            Customer(id=1, name="Alice Johnson", email="alice@example.com"),
            Customer(id=2, name="Bob Smith", email="bob@example.com"),
            Customer(id=3, name="Charlie Brown", email="charlie@example.com"),
            Customer(id=4, name="Diana Prince", email="diana@example.com"),
            Customer(id=5, name="Evan Wright", email="evan@example.com"),
            Customer(id=6, name="Fiona Green", email="fiona@example.com"),
        ]
        session.add_all(customers)
        
        # Add 4 orders
        orders = [
            Order(id=1, customer_id=1, status="completed"),
            Order(id=2, customer_id=2, status="processing"),
            Order(id=3, customer_id=3, status="pending"),
            Order(id=4, customer_id=1, status="shipped"),
        ]
        session.add_all(orders)
        
        # Add order items
        order_items = [
            OrderItem(order_id=1, isbn="9780132350884", qty=1, price=35.99),
            OrderItem(order_id=1, isbn="9780131101633", qty=1, price=39.99),
            OrderItem(order_id=2, isbn="9780201616224", qty=1, price=42.99),
            OrderItem(order_id=3, isbn="9780321125217", qty=1, price=55.99),
            OrderItem(order_id=3, isbn="9780131177055", qty=1, price=37.99),
            OrderItem(order_id=3, isbn="9780596007126", qty=1, price=49.99),
            OrderItem(order_id=4, isbn="9780132350884", qty=2, price=35.99),
            OrderItem(order_id=4, isbn="9780137081073", qty=1, price=48.99),
        ]
        session.add_all(order_items)
        
        # Save everything
        await session.commit()
        
        # Verify counts
        book_count = await session.scalar(text("SELECT COUNT(*) FROM books"))
        customer_count = await session.scalar(text("SELECT COUNT(*) FROM customers"))
        order_count = await session.scalar(text("SELECT COUNT(*) FROM orders"))
        order_item_count = await session.scalar(text("SELECT COUNT(*) FROM order_items"))
        
        print("Seed complete!")
        print(f"Books: {book_count}/10")
        print(f"Customers: {customer_count}/6")
        print(f"Orders: {order_count}/4")
        print(f"Order Items: {order_item_count}")


asyncio.run(seed_database())