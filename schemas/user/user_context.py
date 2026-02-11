from pydantic import BaseModel, EmailStr
from schemas.user.address import Address


class UserContext(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: Address
