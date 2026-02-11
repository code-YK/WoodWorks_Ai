from pydantic import BaseModel, EmailStr
from schemas.user.address import Address


class UserRegistrationInput(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: Address
