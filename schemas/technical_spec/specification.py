from pydantic import BaseModel
from schemas.technical_spec.field import TechnicalSpecField


class TechnicalSpecification(BaseModel):
    fields: list[TechnicalSpecField]
    assumptions: list[str] = []
