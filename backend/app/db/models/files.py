import datetime
import uuid

from sqlalchemy import UniqueConstraint, String, BIGINT, ForeignKey, TIMESTAMP, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import LtreeType

from app.constants import DEFAULT_FILE_GROUP_ICON_ID, DELETED_COMPANY_ID
from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin, BigIntPrimaryKeyMixin


class FilesGroup(Base, UUIDPrimaryKeyMixin):
    """Группы файлов."""

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
    file_group_type_id: Mapped[int] = mapped_column(SMALLINT, comment="Идентификатор типа группы")
    path: Mapped[LtreeType] = mapped_column(LtreeType, comment="Иерархия групп файлов")


class File(Base, UUIDPrimaryKeyMixin):
    """Файлы."""

    __tablename__ = "files"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="SET DEFAULT"), default=DELETED_COMPANY_ID, comment="Идентификатор компании"
    )
    download_file_name: Mapped[str] = mapped_column(comment="Имя файла при скачивание")
    file_name: Mapped[str] = mapped_column(comment="Системное имя файла", unique=True)
    size: Mapped[int] = mapped_column(BIGINT, comment="Размер файла")
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, comment="Время создания")
    updated_at: Mapped[datetime.datetime | None] = mapped_column(TIMESTAMP, comment="Время последнего обновления")
    checksum: Mapped[str] = mapped_column(String(64), comment="Чексумма файла")


class FileInGroup(Base, BigIntPrimaryKeyMixin):
    """Привязка файла к группе."""

    __tablename__ = "files_in_groups"
    __table_args__ = {"constraints": (UniqueConstraint("file_id", "file_group_id", name="uq_file_in_group"),)}

    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), comment="Идентификатор файла"
    )
    # TODO Тригер если групп осталось 0 то помещаем в корзину
    files_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files_groups.id", ondelete="CASCADE"), comment="Идентификатор группы файлов"
    )


class TaskAttachment(Base, BigIntPrimaryKeyMixin):
    """Файлы прикрепленные к задаче."""

    __tablename__ = "task_attachments"
    __table_args__ = {"constraints": (UniqueConstraint("task_id", "file_id", name="uq_task_attachment"),)}

    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), comment="Идентификатор задачи"
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), comment="Идентификатор файла"
    )


class CommentAttachment(Base, BigIntPrimaryKeyMixin):
    """Файлы прикрепленные к комментариям."""

    __tablename__ = "task_attachments"
    __table_args__ = {"constraints": (UniqueConstraint("task_comment_id", "file_id", name="uq_comment_attachment"),)}

    task_comment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("task_comments.id", ondelete="CASCADE"), comment="Идентификатор комментария"
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), comment="Идентификатор файла"
    )


class MessageAttachment(Base, BigIntPrimaryKeyMixin):
    """Файлы прикрепленные к сообщениям в чате."""

    __tablename__ = "task_attachments"
    __table_args__ = {"constraints": (UniqueConstraint("message_id", "file_id", name="uq_message_attachment"),)}

    message_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("message.id", ondelete="CASCADE"), comment="Идентификатор сообщения"
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"), comment="Идентификатор файла"
    )
