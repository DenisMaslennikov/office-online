from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.api.v1.core.schemas import ConfirmSchema
from app.api.v1.dependencies.jwt import get_current_user_id
from app.api.v1.dependencies.users import (
    auth_user,
    get_current_user_with_tz,
    get_user_from_refresh_token,
    validate_user,
)
from app.api.v1.users import crud
from app.api.v1.users.schemas import (
    ChangePasswordSchema,
    JWTTokenForValidationSchema,
    JWTTokensPairWithTokenTypeSchema,
    TokenValidationResultSchema,
    UserCacheSchema,
    UserReadTZSchema,
)
from app.api.v1.users.tools import add_tz_to_user
from app.constants import DEFAULT_RESPONSES
from app.db import db_helper
from app.db.models import User

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
    user: Annotated[User | UserCacheSchema, Depends(get_user_from_refresh_token)]
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
    response_model=UserReadTZSchema,
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
) -> UserReadTZSchema:
    """Создание нового пользователя."""
    user_from_bd = await crud.get_user_by_email_or_username_from_db(session, email, username)
    if user_from_bd is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email или username уже зарегистрирован",
        )
    user_cache = await crud.create_user(
        session=session,
        email=email,
        username=username,
        password=password,
        display_name=display_name,
        phone=phone,
        image=image,
        timezone_id=timezone_id,
    )
    return await add_tz_to_user(user_cache, session)


@router.get("/me/", response_model=UserReadTZSchema, responses=DEFAULT_RESPONSES)
async def get_user_me(user: Annotated[UserReadTZSchema, Depends(get_current_user_with_tz)]) -> UserReadTZSchema:
    """Получение информации о текущем пользователе."""
    return user


@router.delete("/me/", response_model=UserReadTZSchema, responses=DEFAULT_RESPONSES)
async def schedule_deletion_user_me(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> UserReadTZSchema:
    """Удаление текущего авторизированного пользователя."""
    user_cache = await crud.schedule_user_deletion(session, user_id)
    return await add_tz_to_user(user_cache, session)


@router.post("/cancel_deletion_me/", response_model=UserReadTZSchema, responses=DEFAULT_RESPONSES)
async def cancel_deletion_user_me(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> UserReadTZSchema:
    """Отменяет запланированное удаление пользователя."""
    user_cache = await crud.cancel_user_deletion(session, user_id)
    return await add_tz_to_user(user_cache, session)


@router.patch("/me/", response_model=UserReadTZSchema, responses=DEFAULT_RESPONSES)
async def partial_update_user_me(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    email: Annotated[EmailStr | None, Form()] = None,
    username: Annotated[str | None, Form()] = None,
    display_name: Annotated[str | None, Form()] = None,
    phone: Annotated[str | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    timezone_id: Annotated[int | None, Form(description="Передайте ноль чтобы убрать таймзону")] = None,
) -> UserReadTZSchema:
    """Частичное обновление информации о пользователе."""
    user = await crud.get_user_by_id(session, user_id, with_tz=False, cache=False)
    if email is not None:
        user_check = await crud.get_user_by_email_or_username_from_db(session, email=email, exclude_id=user_id)
        if user_check is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой email уже зарегистрирован")
    if username is not None:
        user_check = await crud.get_user_by_email_or_username_from_db(session, username=username, exclude_id=user_id)
        if user_check is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такой username уже зарегистрирован")
    user = await crud.update_user_repo(
        session,
        user,
        email=email,
        username=username,
        display_name=display_name,
        phone=phone,
        image=image,
        timezone_id=timezone_id,
    )
    return await add_tz_to_user(user, session)


@router.post("/change_password/", response_model=ConfirmSchema, responses=DEFAULT_RESPONSES)
async def change_password_me(
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    passwords: ChangePasswordSchema,
) -> ConfirmSchema:
    """Смена пароля текущего пользователя."""
    user = await crud.get_user_by_id(session, user_id, with_tz=False, cache=False)
    validate_user(user)
    if not user.verify_password(passwords.old_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный старый пароль")

    return ConfirmSchema(success=await crud.change_user_password(session, user, passwords.new_password))
