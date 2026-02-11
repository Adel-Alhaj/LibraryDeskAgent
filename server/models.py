from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Text
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# -------------------------
# Books
# -------------------------

class Book(Base):
    __tablename__ = "books"

    isbn = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)

    # Allow access order_items from books: book.order_items
    order_items = relationship("OrderItem", back_populates="book")


# -------------------------
# Customers
# -------------------------

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    # Allow to access orders from customers: customers.orders
    orders = relationship("Order", back_populates="customer")


# -------------------------
# Orders
# -------------------------

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="created")

    # Allow to access customers from orders: orders.customers
    customer = relationship("Customer", back_populates="orders")
    # Allow to items orders from orders: orders.items
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    isbn = Column(String, ForeignKey("books.isbn"), nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    # Allow access orders from order_items: order_items.order
    order = relationship("Order", back_populates="items")
    # Allow access books from order_items: order_items.book
    book = relationship("Book", back_populates="order_items")


# -------------------------
# Chat storage
# -------------------------

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    role = Column(String, nullable=False)  # user | assistant | tool
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    name = Column(String, nullable=False)
    args_json = Column(Text)
    result_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
