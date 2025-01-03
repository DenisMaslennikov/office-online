import uuid

from sqlalchemy import BIGINT, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin


class Tag(Base, BigIntPrimaryKeyMixin):
    """Модель тегов."""

    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="uq_tag_name_by_company"),
        UniqueConstraint("name", "project_id", name="uq_tag_name_by_project"),
        CheckConstraint(
            "(company_id IS NOT NULL AND project_id IS NULL) OR (company_id IS NULL AND project_id IS NOT NULL)",
            name="chk_project_or_company",
        ),
        {"comment": "Теги"},
    )

    name: Mapped[str] = mapped_column(String(30), comment="Название тега")
    description: Mapped[str] = mapped_column(comment="Описание тега")
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )
    color: Mapped[str] = mapped_column(String(9), comment="Цвет тега")

    def __repr__(self):
        return f"<tag {self.name}>"


class TaskTag(Base, BigIntPrimaryKeyMixin):
    """Теги на задачах."""

    __tablename__ = "tasks_tags"
    __table_args__ = (
        UniqueConstraint("tag_id", "task_id", name="uq_task_tag"),
        {"comment": "Теги на задачах"},
    )

    tag_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("tags.id", ondelete="CASCADE"), comment="Идентификатор тега")
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )

    def __repr__(self):
        return f"<TaskTag {self.task_id} - {self.tag_id}>"


class FileTag(Base, BigIntPrimaryKeyMixin):
    """Теги на файлах."""

    __tablename__ = "files_tags"
    __table_args__ = (
        UniqueConstraint("tag_id", "file_id", name="uq_file_tag"),
        {"comment": "Теги на файлах"},
    )

    tag_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("tags.id", ondelete="CASCADE"), comment="Идентификатор тега")
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), comment="Идентификатор файла"
    )

    def __repr__(self):
        return f"<FileTag {self.tag_id} - {self.file_id}>"
