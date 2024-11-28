import datetime
import uuid

from sqlalchemy import UniqueConstraint, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class Board(Base, UUIDPrimaryKeyMixin):
    """Модель доски для учета задач."""

    __tablename__ = "boards"
    __table_args__ = {"constraints": (UniqueConstraint("project_id", "name", name="uq_board_name"),)}

    name: Mapped[str] = mapped_column(String(255), comment="Имя доски")
    description: Mapped[str | None] = mapped_column(comment="Описание доски")
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), comment="идентификатор проекта")
    start_time: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Дата начала")
    end_time: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Дата окончания")
    archived_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Дата архивации")
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, comment="Дата окончания", server_default=func.now()
    )
