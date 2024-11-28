import datetime
import uuid

from sqlalchemy import UniqueConstraint, String, ForeignKey, TIMESTAMP, func, SMALLINT, text
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


class BoardColumn(Base, UUIDPrimaryKeyMixin):
    """Модель столбца доски."""

    __tablename__ = "boards_columns"
    __table_args__ = {"constraints": (UniqueConstraint("board_id", "name", name="uq_column_name"),)}

    name: Mapped[str] = mapped_column(String(100), comment="Имя столбца")
    description: Mapped[str | None] = mapped_column(comment="Описание столбца")
    board_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("boards.id"), comment="Идентификатор доски")
    number: Mapped[int] = mapped_column(SMALLINT, comment="Номер столбца по порядку")
    color: Mapped[str] = mapped_column(String(9), comment="Цвет столбца")
    max_task: Mapped[int] = mapped_column(
        SMALLINT, comment="Ограничение по числу задач в столбце", default=0, server_default=text("0")
    )
    mark_task_as_completed: Mapped[bool] = mapped_column(
        comment="Автоматический помечать задачу как выполненную при перемещение в столбец",
        default=False,
        server_default=text("false"),
    )
