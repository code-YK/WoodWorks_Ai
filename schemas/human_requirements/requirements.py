from pydantic import BaseModel
from schemas.human_requirements.field import HumanRequirementField


class HumanRequirements(BaseModel):
    fields: list[HumanRequirementField]
