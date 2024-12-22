from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.api.v1.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.api.v1.dependencies.users import auth_user, get_user_from_refresh_token, get_current_user
from app.api.v1.users import crud
from app.api.v1.users.schemas import (
    JWTTokenForValidationSchema,
    JWTTokensPairWithTokenTypeSchema,
    TokenValidationResultSchema,
    UserResponseSchema,
    UserCashSchema,
)
from app.constants import DEFAULT_RESPONSES
from app.db import db_helper
from app.db.models import User
from app.utils.redis import update_cash

router = APIRouter(tags=["Users"])


@router.post(
    "/jwt/create/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Ошибка авторизации"},
        status.HTTP_403_FORBIDDEN: {"description": "Аккаунт пользователя не активен"},
    },
)
async def create_tokens(user: Annotated[User, Depends(auth_user)]) -> JWTTokensPairWithTokenTypeSchema:
    """Логин пользователя для получения JWT токенов."""
    return JWTTokensPairWithTokenTypeSchema(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post(
    "/jwt/refresh/",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Некорректный refresh токен"},
        status.HTTP_403_FORBIDDEN: {"description": "Аккаунт пользователя не активен"},
    },
)
async def tokens_refresh(
    user: Annotated[User, Depends(get_user_from_refresh_token)]
) -> JWTTokensPairWithTokenTypeSchema:
    """Обновление токенов по refresh токену."""
    return JWTTokensPairWithTokenTypeSchema(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/jwt/validate/")
async def token_validate(token: JWTTokenForValidationSchema) -> TokenValidationResultSchema:
    """Валидирует токен."""
    try:
        decode_token(token.token)
    except HTTPException:
        return TokenValidationResultSchema(validation_result=False)
    else:
        return TokenValidationResultSchema(validation_result=True)


@router.post(
    "/register/",
    response_model=UserResponseSchema,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Пользователь с таким username или email уже зарегистрирован"},
    },
)
async def user_register(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    email: Annotated[EmailStr, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    display_name: Annotated[str | None, Form()] = None,
    phone: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    timezone_id: Annotated[int | None, Form()] = None,
) -> UserCashSchema:
    """Создание нового пользователя."""
    user_from_bd = await crud.get_user_by_email_or_username_repo(session, email, username)
    if user_from_bd is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email или username уже зарегистрирован",
        )
    user = await crud.create_user_repo(
        session=session,
        email=email,
        username=username,
        password=password,
        display_name=display_name,
        phone=phone,
        image=image,
        timezone_id=timezone_id,
    )
    response = UserCashSchema.model_validate(user)
    await update_cash(settings.redis.user_prefix, response)
    return response


@router.get("/me/", response_model=UserResponseSchema, responses=DEFAULT_RESPONSES)
async def get_user_me(user: Annotated[UserCashSchema, Depends(get_current_user)]) -> UserCashSchema:
    """Получение информации о текущем пользователе."""
    return user
