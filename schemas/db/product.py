from pydantic import BaseModel
from schemas.base.enums import ProductCategory


class ProductCreate(BaseModel):
    name: str
    category: ProductCategory


class ProductRead(ProductCreate):
    id: int

    model_config = {
        "from_attributes": True
    }
