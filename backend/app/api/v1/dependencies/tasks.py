from typing import Annotated
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.v1.dependencies.users import get_current_user
from app.api.v1.tasks import crud
from app.db import db_helper
from app.db.models import Task, User


async def get_task_by_id_for_current_user(
    task_id: UUID,
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> Task:
    """Получение задачи по id для текущего пользователя."""
    task = await crud.get_task_by_id_repo(session, task_id, joinedload(Task.task_status))
    if task is None or task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task
