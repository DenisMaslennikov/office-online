from pydantic import BaseModel


class ConfirmSchema(BaseModel):
    """Схема для подтверждения успешности действия."""

    success: bool
