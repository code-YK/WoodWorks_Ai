from datetime import datetime
from pydantic import BaseModel


class ConfirmationFlags(BaseModel):
    human_requirements_confirmed: bool = False
    order_confirmed: bool = False

    human_confirmed_at: datetime | None = None
    order_confirmed_at: datetime | None = None
