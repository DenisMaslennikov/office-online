import uuid

from sqlalchemy import BIGINT, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DEFAULT_PROJECT_ICON_ID
from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class Project(Base, UUIDPrimaryKeyMixin):
    """Модель проекта."""

    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="uq_project_name"),
        UniqueConstraint("prefix", "company_id", name="uq_project_prefix"),
        {"comment": "Таблица проектов"},
    )

    name: Mapped[str] = mapped_column(String(255), comment="Название проекта")
    prefix: Mapped[str] = mapped_column(String(50), comment="Префикс проекта")
    description: Mapped[str | None] = mapped_column(comment="Описание проекта")
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), comment="Идентификатор организации")
    icon_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("icons.id", ondelete="SET DEFAULT"),
        comment="Иконка проекта",
        default=DEFAULT_PROJECT_ICON_ID,
    )

    def __repr__(self):
        return f"<Project {self.name}>"
