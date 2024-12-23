import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

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


class UserWithoutTimezoneSchema(BaseUserSchema):
    """Сериализатор пользователя без информации о его часовом поясе."""

    id: UUID
    image: str | None = Field(exclude=True)
    is_bot: bool
    active: bool
    scheduled_deletion_date: datetime.datetime | None

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
    active: bool
    timezone: TimezoneReadSchema | None
    is_bot: bool
    scheduled_deletion_date: datetime.datetime | None


class UserResponseSchema(UserWithoutTimezoneSchema):
    """Сериализатор пользователя для операций чтения."""

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
