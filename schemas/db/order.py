from pydantic import BaseModel
from typing import List, Dict, Any


class OrderCreate(BaseModel):
    user_id: int
    items: List["OrderItemCreate"]
    total_price: float
    currency: str


class OrderItemCreate(BaseModel):
    product_id: int
    technical_spec: Dict[str, Any]
    unit_price: float
    quantity: int
