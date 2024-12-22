from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.api.v1.dependencies.jwt import get_current_user_id, get_user_id_from_refresh_token
from app.api.v1.users import crud
from app.api.v1.users.schemas import UserLoginSchema, UserResponseSchema, UserCashSchema
from app.db import db_helper
from app.db.models import User
from app.utils.redis import get_from_cash, update_cash


async def user_is_active(user: User | UserCashSchema) -> bool:
    """Проверяет активен ли пользователь."""
    if user.active is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт пользователя не активен")
    return True


async def auth_user(
    user_credentials: UserLoginSchema, session: Annotated[AsyncSession, Depends(db_helper.get_session)]
) -> User:
    """Возвращает авторизованного пользователя."""
    user = await crud.get_user_by_email_repo(session, user_credentials.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный email или пароль")
    if not user.verify_password(user_credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный email или пароль")

    await user_is_active(user)

    return user


async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> UserCashSchema:
    """Получает текущего пользователя."""
    user_from_cash = await get_from_cash(settings.redis.user_prefix, user_id, UserCashSchema)
    if user_from_cash is not None:
        await user_is_active(user_from_cash)
        return user_from_cash

    user_from_db = await crud.get_user_by_id_repo(session, user_id=user_id)
    user = UserCashSchema.model_validate(user_from_db)
    await update_cash(settings.redis.user_prefix, user)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    await user_is_active(user)
    return user


async def get_user_from_refresh_token(
    user_id: Annotated[UUID, Depends(get_user_id_from_refresh_token)],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> User:
    """Получает объект пользователя из рефреш токена."""
    user_from_cash = await get_from_cash(settings.redis.user_prefix, user_id, UserCashSchema)
    if user_from_cash is not None:
        return user_from_cash

    user = await crud.get_user_by_id_repo(session, user_id=user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    await user_is_active(user)
    return user
