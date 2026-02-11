from pydantic import BaseModel


class PricingLineItem(BaseModel):
    item_code: str
    description: str
    quantity: float
    unit_price: float
    total_price: float
    in_stock: bool
