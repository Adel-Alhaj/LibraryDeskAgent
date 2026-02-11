from pydantic import BaseModel, Field
from typing import List, Optional
#from datetime import datetime


# # -------------------------
# # Books
# # -------------------------

# class BookBase(BaseModel):
#     isbn: str
#     title: str
#     author: str
#     price: float
#     stock: int


# class BookResponse(BookBase):
#     pass


# class FindBooksRequest(BaseModel):
#     q: str = Field(..., description="Search query")
#     by: str = Field(..., description="Search field: title or author")


# # -------------------------
# # Customers
# # -------------------------

# class CustomerBase(BaseModel):
#     id: int
#     name: str
#     email: str


# class CustomerResponse(CustomerBase):
#     pass


# # -------------------------
# # Orders
# # -------------------------

# class OrderItemCreate(BaseModel):
#     isbn: str
#     qty: int = Field(..., gt=0)


# class CreateOrderRequest(BaseModel):
#     customer_id: int
#     items: List[OrderItemCreate]


# class CreateOrderResponse(BaseModel):
#     order_id: int
#     total_items: int


# class OrderItemResponse(BaseModel):
#     isbn: str
#     title: str
#     qty: int
#     price: float


# class OrderStatusResponse(BaseModel):
#     order_id: int
#     customer_id: int
#     status: str
#     items: List[OrderItemResponse]
#     created_at: datetime


# # -------------------------
# # Inventory
# # -------------------------

# class RestockBookRequest(BaseModel):
#     isbn: str
#     qty: int = Field(..., gt=0)


# class UpdatePriceRequest(BaseModel):
#     isbn: str
#     price: float = Field(..., gt=0)


# class InventoryItem(BaseModel):
#     isbn: str
#     title: str
#     stock: int


# class InventorySummaryResponse(BaseModel):
#     low_stock: List[InventoryItem]


# -------------------------
# Chat & Agent
# -------------------------

# class ChatMessage(BaseModel):
#     role: str  # "user" | "assistant" | "tool"
#     content: str


class ChatRequest(BaseModel):
    session_id: Optional[str]
    message: str


# class ChatResponse(BaseModel):
#     session_id: str
#     reply: str


# -------------------------
# Pydantic schemas for complex tool inputs
# -------------------------
class OrderItemInput(BaseModel):
    """Schema for a single order item"""
    isbn: str = Field(description="ISBN of the book")
    qty: int = Field(description="Quantity to order")

class CreateOrderInput(BaseModel):
    """Schema for creating an order"""
    customer_id: int = Field(description="Customer ID")
    items: List[OrderItemInput] = Field(description="List of items to order with isbn and qty")
