from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    session_id: Optional[str]
    message: str


class OrderItemInput(BaseModel):
    """Schema for a single order item"""
    isbn: str = Field(description="ISBN of the book")
    qty: int = Field(description="Quantity to order")

class CreateOrderInput(BaseModel):
    """Schema for creating an order"""
    customer_id: int = Field(description="Customer ID")
    items: List[OrderItemInput] = Field(description="List of items to order with isbn and qty")
