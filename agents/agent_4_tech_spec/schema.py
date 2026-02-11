from pydantic import BaseModel


class TechSpecOverrideInput(BaseModel):
    force_material: str | None = None
    force_thickness_mm: int | None = None
