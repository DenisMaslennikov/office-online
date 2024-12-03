import datetime
import uuid

from sqlalchemy import String, ForeignKey, TIMESTAMP, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base
from app.db.models.enums import sprint_status_enum
from app.db.models.mixins import BigIntPrimaryKeyMixin


class Sprint(Base, BigIntPrimaryKeyMixin):
    """Модель спринта."""

    __tablename__ = "sprints"

    name: Mapped[str] = mapped_column(String(100), comment="Название спринта")
    description: Mapped[str] = mapped_column(comment="Описание/цель спринта")
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )
    start_date: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Время начала спринта")
    end_date: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Время завершения спринта")
    status: Mapped[str] = mapped_column(sprint_status_enum, comment="Статус спринта", default="Планирование")
    story_points: Mapped[int | None] = mapped_column(BIGINT, comment="Стори поинты спринта")


class TasksSprint(Base, BigIntPrimaryKeyMixin):
    """Задачи спринта."""

    __tablename__ = "tasks_sprints"

    sprint_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("sprints.id", ondelete="CASCADE"), comment="Идентификатор спринта"
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )
