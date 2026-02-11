from pydantic import BaseModel
from schemas.base.enums import FieldValueType


class HumanRequirementField(BaseModel):
    key: str
    label: str
    value: str | int | float | bool | None
    value_type: FieldValueType
    unit: str | None = None
    required: bool = False
