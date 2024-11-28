import datetime
import uuid

from sqlalchemy import String, ForeignKey, TIMESTAMP, BIGINT, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class Task(Base, UUIDPrimaryKeyMixin):
    """Модель задачи."""

    __tablename__ = "tasks"
    __table_args__ = {"constraints": (UniqueConstraint("project_id", "name", name="uq_task_name"),)}

    name: Mapped[str] = mapped_column(String(255), comment="Название задачи")
    description: Mapped[str] = mapped_column(comment="Описание задачи")
    column_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("boards_columns.id", ondelete="RESTRICT"), comment="Идентификатор столбца"
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )
    color: Mapped[str] = mapped_column(String(9), comment="Цвет задачи")
    deadline: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Выполнить до")
    task_type_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("task_types.id", ondelete="RESTRICT"), comment="Идентификатор типа задачи"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=func.now(), comment="Создана")
    updated_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Обновлена")
    completed_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Выполнена")
    archived_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Архивирована")
