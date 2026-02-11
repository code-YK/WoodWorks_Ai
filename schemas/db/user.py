from pydantic import BaseModel, EmailStr
from schemas.user.address import Address


class UserCreate(BaseModel):
    """
    Used ONLY before inserting into DB
    """
    name: str
    email: EmailStr
    phone: str
    address: Address


class UserRead(BaseModel):
    """
    Used when reading from DB
    """
    id: int
    name: str
    email: EmailStr
    phone: str
    address: Address

    model_config = {
        "from_attributes": True
    }
