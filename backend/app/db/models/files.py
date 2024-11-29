import uuid

from sqlalchemy import UniqueConstraint, String, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DEFAULT_FILE_GROUP_ICON_ID
from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class FilesGroup(Base, UUIDPrimaryKeyMixin):
    """Категории файлов."""

    __tablename__ = "files_groups"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", name="uq_file_group_name"),)}

    name: Mapped[str] = mapped_column(String(255), comment="Имя группы файлов")
    description: Mapped[str | None] = mapped_column(comment="Описание группы файлов")
    icon_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("icons.id", ondelete="SET DEFAULT"),
        default=DEFAULT_FILE_GROUP_ICON_ID,
        comment="Иконка группы файлов",
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
