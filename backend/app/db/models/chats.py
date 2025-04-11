import datetime
import uuid

from sqlalchemy import BIGINT, SMALLINT, TIMESTAMP, CheckConstraint, ForeignKey, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DELETED_MESSAGE_ID, DELETED_USER_ID
from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin, UUIDPrimaryKeyMixin


class ChannelsGroup(Base, UUIDPrimaryKeyMixin):
    """Группы каналов."""

    __tablename__ = "channels_groups"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="uq_channels_group_name"),
        {"comment": "Группы каналов"},
    )

    name: Mapped[str] = mapped_column(String(30), comment="Имя группы")
    description: Mapped[str] = mapped_column(comment="Описание группы")
    # path: Mapped[LtreeType] = mapped_column(LtreeType, comment="Иерархия группы")
    parent_channel_group_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("channels_groups.id", ondelete="CASCADE"), comment="Родительская группа каналов"
    )
    permissions_parent_channel_group_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("channels_groups.id", ondelete="CASCADE"), comment="Группа каналов от которой наследуются права"
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    system: Mapped[bool] = mapped_column(comment="Является системной")
    order: Mapped[int] = mapped_column(SMALLINT, comment="Порядок при сортировке")
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )

    def __repr__(self):
        return f"<ChannelsGroup {self.name}>"


class Channel(Base, UUIDPrimaryKeyMixin):
    """Каналы."""

    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="uq_channel_name"),
        CheckConstraint(
            '''
            (channel_group_id IS NOT NULL AND project_id IS NULL)
            OR
            (channel_group_id IS NULL AND project_id IS NOT NULL)
            ''',
            name="check_channel_group_project_xor",
        ),
        {"comment": "Каналы"},
    )

    name: Mapped[str | None] = mapped_column(String(30), comment="Название канала")
    description: Mapped[str] = mapped_column(comment="Описание канала")
    channel_group_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("channels_groups.id", ondelete="CASCADE"), comment="Идентификатор группы каналов"
    )
    permissions_parent_channel_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels_groups.id", ondelete="CASCADE"),
        comment="Группа каналов от которой наследуются права на канал",
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор компании"
    )
    order: Mapped[int] = mapped_column(SMALLINT, comment="Порядок при сортировке")
    system: Mapped[bool] = mapped_column(comment="Системный канал")
    private: Mapped[bool] = mapped_column(comment="Приватный чат")
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )

    def __repr__(self):
        return f"<Channel {self.name}>"


class Message(Base, BigIntPrimaryKeyMixin):
    """Модель сообщения."""

    __tablename__ = "messages"

    content: Mapped[str] = mapped_column(comment="Содержимое сообщения")
    channel_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), comment="Идентификатор канала"
    )
    thread_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("threads.id", ondelete="CASCADE"), comment="Идентификатор треда"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        comment="Идентификатор пользователя",
        default=DELETED_USER_ID,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), comment="Время создания сообщения"
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), comment="Время последнего изменения сообщения"
    )
    quoted_message_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("messages.id", ondelete="SET DEFAULT"),
        default=DELETED_MESSAGE_ID,
        comment="Идентификатор цитируемого сообщения",
    )
    is_deleted: Mapped[bool] = mapped_column(
        comment="Сообщение помечено как удаленное",
        default=False,
        server_default=text("false"),
    )

    def __repr__(self):
        return f"<Message {self.id}: {self.content}>"


class LastReadMessageByUser(Base, BigIntPrimaryKeyMixin):
    """Модель хранящая последнее прочитанное сообщение в чате для пользователя."""

    __tablename__ = "last_read_message_by_user"
    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="uq_last_read_message_by_user_chanel"),
        {"comment": "Таблица хранящая последнее прочитанное сообщение в чате для пользователя."},
    )

    message_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("messages.id", ondelete="CASCADE"), comment="Идентификатор сообщения"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    channel_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), comment="Идентификатор канала"
    )
    thread_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("threads.id", ondelete="CASCADE"), comment="Идентификатор треда"
    )

    def __repr__(self):
        return f"<LastReadMessageByUser {self.user_id}: {self.channel_id} - {self.message_id}>"


class Thread(Base, BigIntPrimaryKeyMixin):
    """Модель для хранения тредов."""

    __tablename__ = "threads"
    parent_message_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("messages.id", ondelete="SET DEFAULT"),
        default=DELETED_MESSAGE_ID,  # TODO подумать где будет выводится тред если родительское сообщение удалено.
    )
    title: Mapped[str] = mapped_column(comment="Заголовок треда")
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        default=datetime.datetime.now,
        comment="Время создания треда",
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), comment="Идентификатор канала"
    )
