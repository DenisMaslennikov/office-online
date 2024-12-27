import uuid
from datetime import datetime, timezone
from pprint import pprint
from uuid import UUID

from fastapi import UploadFile
from pydantic import EmailStr
from sqlalchemy import Result, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from app.api.v1.users.schemas import UserCacheSchema, UserReadTZSchema
import app.api.v1.classifiers.crud as classifiers_crud
from app.config import settings
from app.constants import USER_IMAGE
from app.db.models import User
from app.db.redis import get_raw_data_from_cache, update_object_cache
from app.utils.file_utils import delete_file, save_file, validate_file_extension, validate_file_size


async def create_user(
    session: AsyncSession,
    email: str,
    username: str,
    display_name: str,
    password: str,
    phone: str | None = None,
    image: UploadFile | None = None,
    timezone_id: int | None = None,
) -> UserCacheSchema:
    """Создание нового пользователя."""
    user = User(
        email=email,
        username=username,
        display_name=display_name,
        phone=phone,
        timezone_id=timezone_id,
    )
    user.password = password
    if image is not None:
        validate_file_size(image, USER_IMAGE)
        validate_file_extension(image, USER_IMAGE)
        user.image = await save_file(image, settings.files.users_images_path)
    session.add(user)
    await session.commit()
    user_cache = UserCacheSchema.model_validate(user)
    await update_object_cache(settings.redis.user_prefix, user_cache)
    return user_cache


async def get_user_by_email(session: AsyncSession, email: str, with_tz: bool = False) -> User | None:
    """Получает пользователя по его email."""
    stmt = select(User).where(User.email == email)
    if with_tz:
        stmt = stmt.options(joinedload(User.timezone_id))
    results = await session.execute(stmt)
    user_cache = UserCacheSchema.model_validate(results)
    await update_object_cache(settings.redis.user_prefix, user_cache)
    return results.scalar()


async def get_user_by_email_or_username_from_db(
    session: AsyncSession,
    email: str,
    username: str,
    with_tz: bool = False,
) -> User | None:
    """Получает пользователя по его email или username."""
    stmt = select(User).where(or_(User.email == email, User.username == username))
    if with_tz:
        stmt = stmt.options(joinedload(User.timezone))
    results: Result = await session.execute(stmt)
    return results.scalars().first()


async def _get_user_by_id_from_db(session: AsyncSession, user_id: UUID, with_tz: bool = False) -> User | None:
    """Получение пользователя из бд."""
    stmt = select(User).where(User.id == user_id)
    if with_tz:
        stmt = stmt.options(joinedload(User.timezone))
    results = await session.execute(stmt)
    return results.scalar()


async def get_user_by_id(
    session: AsyncSession, user_id: UUID, cache: bool = True, with_tz: bool = False
) -> User | UserCacheSchema | UserReadTZSchema | None:
    """Возвращает пользователя с заданным id."""
    if not cache:
        return await _get_user_by_id_from_db(session, user_id, with_tz)

    user_raw_cache = await get_raw_data_from_cache(settings.redis.user_prefix, user_id)
    if user_raw_cache is not None:
        if with_tz:
            user_raw_cache["timezone"] = await classifiers_crud.get_timezone_by_id(
                session, user_raw_cache["timezone_id"]
            )
            user_cache = UserReadTZSchema(**user_raw_cache)
        else:
            user_cache = UserCacheSchema(**user_raw_cache)
        return user_cache

    user = await _get_user_by_id_from_db(session, user_id, with_tz)
    await update_object_cache(settings.redis.user_prefix, UserCacheSchema.model_validate(user))
    if with_tz:
        user_cache = UserReadTZSchema.model_validate(user)
    else:
        user_cache = UserCacheSchema.model_validate(user)
    return user_cache


async def schedule_user_deletion(session: AsyncSession, user_id: uuid.UUID) -> UserCacheSchema:
    """Добавляет пользователя в очередь на удаление."""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(scheduled_deletion_date=datetime.now(timezone.utc) + settings.users.user_deletion_timedelta)
        .returning(User)
    )
    result = await session.execute(stmt)
    updated_user = result.scalar_one()
    await session.commit()
    user_cache = UserCacheSchema.model_validate(updated_user)
    await update_object_cache(settings.redis.user_prefix, user_cache)
    return user_cache


async def update_user_repo(
    session: AsyncSession,
    user: User,
    email: EmailStr | None = None,
    username: str | None = None,
    display_name: str | None = None,
    phone: str | None = None,
    image: UploadFile | None = None,
    timezone_id: int | None = None,
) -> UserCacheSchema:
    """Частичное обновление информации о пользователе."""
    if email is not None:
        user.email = email
    if username is not None:
        user.username = username
    if display_name is not None:
        user.display_name = display_name
    if phone is not None:
        user.phone = phone
    if image is not None:
        validate_file_size(image, USER_IMAGE)
        validate_file_extension(image, USER_IMAGE)
        if user.image is not None:
            await delete_file(user.image, settings.files.users_images_path)
        user.image = await save_file(image, settings.files.users_images_path)
    if timezone_id is not None:
        user.timezone_id = timezone_id
    await session.commit()
    await session.refresh(user)
    user_cache = UserCacheSchema.model_validate(user)
    await update_object_cache(settings.redis.user_prefix, user_cache)
    return user_cache


async def cancel_user_deletion(session: AsyncSession, user_id: uuid.UUID) -> UserCacheSchema:
    """Отменяет удаление пользователя."""
    stmt = update(User).where(User.id == user_id).values(scheduled_deletion_date=None).returning(User)
    result = await session.execute(stmt)
    updated_user = result.scalar_one()
    await session.commit()
    user_cache = UserCacheSchema.model_validate(updated_user)
    await update_object_cache(settings.redis.user_prefix, user_cache)
    return user_cache
