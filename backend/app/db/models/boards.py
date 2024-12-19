import datetime
import uuid

from sqlalchemy import SMALLINT, TIMESTAMP, CheckConstraint, ForeignKey, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class Board(Base, UUIDPrimaryKeyMixin):
    """Модель доски для учета задач."""

    __tablename__ = "boards"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_board_name"),
        {"comment": "Модель доски для учета задач."},
    )

    name: Mapped[str] = mapped_column(String(255), comment="Имя доски")
    description: Mapped[str | None] = mapped_column(comment="Описание доски")
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="идентификатор проекта"
    )
    archived_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP(timezone=True), comment="Дата архивации")
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), comment="Дата создания", server_default=func.now()
    )

    def __repr__(self):
        return f"<Board {self.name}>"


class BoardColumn(Base, UUIDPrimaryKeyMixin):
    """Модель столбца доски."""

    __tablename__ = "boards_columns"
    __table_args__ = (
        UniqueConstraint("board_id", "name", name="uq_column_name"),
        {"comment": "Таблица столбца доски"},
    )

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

    def __repr__(self):
        return f"<BoardColumn {self.name}>"


class BoardTemplate(Base, UUIDPrimaryKeyMixin):
    """Модель шаблона доски."""

    __tablename__ = "boards_templates"
    __table_args__ = (
        UniqueConstraint("project_id", "name", name="uq_board_template_name_for_project"),
        UniqueConstraint("company_id", "name", name="uq_board_template_name_for_company"),
        CheckConstraint(
            "(company_id IS NOT NULL AND project_id IS NULL) OR (company_id IS NULL AND project_id IS NOT NULL)",
            name="chk_company_or_project",
        ),
        {"comment": "Таблица шаблонов досок"},
    )

    name: Mapped[str] = mapped_column(String(255), comment="Имя шаблона доски")
    description: Mapped[str | None] = mapped_column(comment="Описание доски")
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )

    def __repr__(self):
        return f"<BoardTemplate {self.name}>"


class BoardsTemplatesColumns(Base, UUIDPrimaryKeyMixin):
    """Модель столбцов для шаблонов досок."""

    __tablename__ = "boards_templates_columns"
    __table_args__ = (
        UniqueConstraint("board_template_id", "name", name="uq_board_templates_name"),
        {"comment": "Таблица столбцов для шаблонов досок"},
    )

    board_template_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("boards_templates.id", ondelete="CASCADE"), comment="Идентификатор шаблона доски"
    )
    name: Mapped[str] = mapped_column(String(100), comment="Имя столбца")
    description: Mapped[str | None] = mapped_column(comment="Описание столбца")
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

    def __repr__(self):
        return f"<BoardsTemplatesColumns {self.name}>"
