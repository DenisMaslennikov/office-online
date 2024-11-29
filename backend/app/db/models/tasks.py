import datetime
import uuid

from sqlalchemy import String, ForeignKey, TIMESTAMP, BIGINT, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin, BigIntPrimaryKeyMixin


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


class ChildTask(Base, BigIntPrimaryKeyMixin):
    """Дочерние задачи."""

    __tablename__ = "child_tasks"

    parent_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор родительской задачи"
    )
    child_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор дочерней задачи"
    )


class TaskResponsible(Base, BigIntPrimaryKeyMixin):
    """Ответственные за задачу."""

    __tablename__ = "task_responsibles"
    __table_args__ = {"constraints": (UniqueConstraint("user_id", "task_id", name="uq_task_responsible"),)}

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя ответственного за задачу"
    )


class TaskComment(Base, UUIDPrimaryKeyMixin):
    """Модель комментария к задаче."""

    __tablename__ = "task_comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        # TODO записать в default id специального пользователя "удаленный пользователь"
        default="dddddddd-dddd-dddd-dddd-dddddddddddd",
        comment="Идентификатор пользователя создавшего комментарий",
    )
    content: Mapped[str] = mapped_column(comment="Содержание комментария")
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, comment="Дата и время создания комментария", server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP, comment="Дата и время последнего обновления комментария"
    )
