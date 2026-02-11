from pydantic import BaseModel


class ValidationException(BaseModel):
    error_code: str
    message: str
    source_agent: str
    requires_human: bool = True
