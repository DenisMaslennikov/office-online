from pydantic import BaseModel, Field


class TimezoneReadSchema(BaseModel):
    """Схема сериализации таймзон для чтения."""

    id: int
    display_name: str
