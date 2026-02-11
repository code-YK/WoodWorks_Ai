from pydantic import BaseModel
from schemas.pricing.line_item import PricingLineItem


class PricingContext(BaseModel):
    items: list[PricingLineItem]
    total_price: float
    currency: str = "INR"
    estimated_delivery_days: int | None = None
