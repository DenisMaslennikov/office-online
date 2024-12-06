from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.v1.classifiers.schemas import TimezoneReadSchema


class UserLoginSchema(BaseModel):
    """Сериализатор для логина пользователя."""

    email: EmailStr = Field(..., examples=["username@example.com"])
    password: str = Field(..., examples=["password"])


class UserReadSchema(BaseModel):
    """Сериализатор пользователя для операций чтения."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    display_name: str
    phone: str
    image: str
    timezone: TimezoneReadSchema
    is_bot: bool


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
