from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.api.v1.dependencies.jwt import user_id_from_refresh_token
from app.api.v1.dependencies.users import auth_user
from app.api.v1.users import crud
from app.api.v1.users.schemas import (
    JWTTokenForValidationSchema,
    JWTTokensPairWithTokenTypeSchema,
    TokenValidationResultSchema,
    UserResponseSchema,
)
from app.db import db_helper
from app.db.models import User

router = APIRouter(tags=["Users"])


@router.post(
    "/jwt/create/",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Ошибка авторизации"}},
)
async def create_tokens(user: Annotated[User, Depends(auth_user)]) -> JWTTokensPairWithTokenTypeSchema:
    """Логин пользователя для получения JWT токенов."""
    return JWTTokensPairWithTokenTypeSchema(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post(
    "/jwt/refresh/",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Некорректный refresh токен"}},
)
async def tokens_refresh(
    user_id: Annotated[UUID, Depends(user_id_from_refresh_token)]
) -> JWTTokensPairWithTokenTypeSchema:
    """Обновление токенов по refresh токену."""
    return JWTTokensPairWithTokenTypeSchema(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
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
    display_name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    phone: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    timezone_id: Annotated[int | None, Form()] = None,
) -> User:
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
    return user
