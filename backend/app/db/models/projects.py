import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class Project(Base, UUIDPrimaryKeyMixin):
    """Модель проекта."""

    __tablename__ = "projects"
    __table_args__ = {
        "constraints": (
            UniqueConstraint("name", "company_id", name="uq_project_name"),
            UniqueConstraint("prefix", "company_id", name="uq_project_prefix"),
        )
    }

    name: Mapped[str] = mapped_column(String(255), comment="Название проекта")
    prefix: Mapped[str] = mapped_column(String(50), comment="Префикс проекта")
    description: Mapped[str | None] = mapped_column(comment="Описание проекта")
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("companies.id"), comment="Идентификатор организации")
