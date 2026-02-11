from pydantic import BaseModel


class TechnicalSpecField(BaseModel):
    key: str
    value: str | int | float | bool
    unit: str | None = None
    derived: bool = True
