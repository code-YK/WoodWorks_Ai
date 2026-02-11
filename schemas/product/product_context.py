from pydantic import BaseModel
from schemas.base.enums import ProductCategory


class ProductContext(BaseModel):
    product_id: int
    category: ProductCategory
    variant: str | None = None