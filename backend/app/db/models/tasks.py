import datetime
import uuid

from sqlalchemy import BIGINT, TIMESTAMP, ForeignKey, Interval, String, UniqueConstraint, func, Integer
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DELETED_USER_ID
from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin, UUIDPrimaryKeyMixin


class Task(Base, UUIDPrimaryKeyMixin):
    """Модель задачи."""

    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_task_name"),
        {"comment": "Задача"},
    )

    name: Mapped[str] = mapped_column(String(255), comment="Название задачи")
    description: Mapped[str] = mapped_column(comment="Описание задачи")
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"), default=DELETED_USER_ID, comment="Идентификатор автора задачи"
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        default=DELETED_USER_ID,
        comment="Идентификатор пользователя которому назначена задача",
    )
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
    archived_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        default=DELETED_USER_ID,
        comment="Идентификатор пользователя архивировавшего задачу",
    )
    time_estimate: Mapped[int | None] = mapped_column(BIGINT, comment="Оценка времени выполнения")
    story_points: Mapped[int | None] = mapped_column(BIGINT, comment="Оценка задачи в story points")

    def __repr__(self):
        return f"<Task {self.project_id} - {self.name}>"


class ChildTask(Base, BigIntPrimaryKeyMixin):
    """Дочерние задачи."""

    __tablename__ = "child_tasks"

    parent_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор родительской задачи"
    )
    child_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор дочерней задачи"
    )

    def __repr__(self):
        return f"<ChildTask {self.parent_task_id} - {self.child_task_id}>"


# class TaskResponsible(Base, BigIntPrimaryKeyMixin):
#     """Ответственные за задачу."""
#
#     __tablename__ = "task_responsibles"
#     __table_args__ = (
#         UniqueConstraint("user_id", "task_id", name="uq_task_responsible"),
#         {"comment": "Ответственные за задачу"},
#     )
#
#     task_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
#     )
#     user_id: Mapped[uuid.UUID] = mapped_column(
#         ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя ответственного за задачу"
#     )
#
#     def __repr__(self):
#         return f"<TaskResponsible {self.task_id} - {self.user_id}>"


class TaskComment(Base, UUIDPrimaryKeyMixin):
    """Модель комментария к задаче."""

    __tablename__ = "task_comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        default=DELETED_USER_ID,
        comment="Идентификатор пользователя создавшего комментарий",
    )
    content: Mapped[str] = mapped_column(comment="Содержание комментария")
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, comment="Дата и время создания комментария", server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP, comment="Дата и время последнего обновления комментария"
    )

    def __repr__(self):
        return f"<TaskComment {self.task_id}({self.user_id}) - {self.content}>"


class LinkedTask(Base, BigIntPrimaryKeyMixin):
    """Связанные задачи."""

    __tablename__ = "linked_tasks"

    from_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Задача с которой стоит связь"
    )
    to_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Задача на которую стоит связь"
    )
    task_link_type_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("task_link_types.id", ondelete="RESTRICT"), comment="Тип связи"
    )

    def __repr__(self):
        return f"<LinkedTask {self.from_task_id} - {self.to_task_id} ({self.task_link_type_id})>"


class TaskTimeSpend(Base, BigIntPrimaryKeyMixin):
    """Учет времени потраченного на задачу"""

    __tablename__ = "task_time_spend"
    description: Mapped[str] = mapped_column(comment="Описание")
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )
    time_spend: Mapped[int] = mapped_column(BIGINT, comment="Потраченое время в минутах")

    def __repr__(self):
        return f"<TaskTimeSpend {self.task_id} - {self.time_spend} ({self.description})>"
