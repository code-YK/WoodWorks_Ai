from pydantic import BaseModel


class Address(BaseModel):
    line_1: str
    line_2: str | None = None
    city: str
    state: str
    pincode: str
