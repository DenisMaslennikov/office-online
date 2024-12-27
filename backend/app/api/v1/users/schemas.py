import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app import db_helper
from app.api.v1.classifiers.crud import get_timezone_by_id
from app.api.v1.classifiers.schemas import TimezoneReadSchema
from app.config import settings


class UserLoginSchema(BaseModel):
    """Сериализатор для логина пользователя."""

    email: EmailStr = Field(..., examples=["username@example.com"])
    password: str = Field(..., examples=["password"])


class BaseUserSchema(BaseModel):
    """Базовая модель пользователя."""

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    username: str
    display_name: str | None
    phone: str | None
    image: str | None
    timezone_id: int | None
    scheduled_deletion_date: datetime.datetime | None
    active: bool
    is_bot: bool


class UserWithoutTZSchema(BaseUserSchema):
    """Сериализатор пользователя без информации о его часовом поясе."""

    id: UUID
    image: str | None = Field(exclude=True)

    @computed_field
    @property
    def image_url(self) -> str | None:
        """Получение url для файла изображения."""
        if self.image is None:
            return None
        return f"{settings.files_urls.users_images_url}{self.image}"


class UserCashSchema(BaseUserSchema):
    """Сериализатор для кеширования пользователя."""

    id: UUID


class UserReadTZSchema(UserWithoutTZSchema):
    """Сериализатор пользователя для операций чтения с информацией о таймзоне."""

    timezone_id: int | None = Field(exclude=True)
    timezone: TimezoneReadSchema | None


class JWTTokensPairBaseSchema(BaseModel):
    """Пара из refresh и access токенов."""

    access_token: str
    refresh_token: str


class JWTTokensPairWithTokenTypeSchema(JWTTokensPairBaseSchema):
    """Пара из refresh и access токенов с указанием типа токенов."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class JWTTokenForValidationSchema(BaseModel):
    """Токен для валидации."""

    token: str


class RefreshTokenSchema(BaseModel):
    """Refresh токен."""

    refresh_token: str


class TokenValidationResultSchema(BaseModel):
    """Результат валидации токена."""

    validation_result: bool
