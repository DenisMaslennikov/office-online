from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.jwt import get_current_user_id, get_user_id_from_refresh_token
from app.api.v1.users import crud
from app.api.v1.users.schemas import UserLoginSchema
from app.db import db_helper
from app.db.models import User


async def auth_user(
    user_credentials: UserLoginSchema, session: Annotated[AsyncSession, Depends(db_helper.get_session)]
) -> User:
    """Возвращает авторизованного пользователя."""
    user = await crud.get_user_by_email_repo(session, user_credentials.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный email или пароль")
    if not user.verify_password(user_credentials.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный email или пароль")
    if user.active is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт пользователя не активен")
    return user


async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> User:
    """Получает текущего пользователя."""
    user = await crud.get_user_by_id_repo(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if not user.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь не активен")
    return user


async def get_user_from_refresh_token(
    user_id: Annotated[UUID, Depends(get_user_id_from_refresh_token)],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> User:
    """Получает объект пользователя из рефреш токена."""
    user = await crud.get_user_by_id_repo(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if user.active is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт пользователя не активен")
    return user
