from pydantic import BaseModel, ConfigDict


class TimezoneReadSchema(BaseModel):
    """Схема сериализации таймзон для чтения."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str


class TimezoneCacheSchema(BaseModel):
    """Схема для кеширования информации о TZ."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    display_name: str
    iana_name: str
