import datetime
import uuid

from sqlalchemy import BIGINT, SMALLINT, TIMESTAMP, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DELETED_MESSAGE_ID, DELETED_USER_ID
from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin, UUIDPrimaryKeyMixin


class ChannelsGroup(Base, UUIDPrimaryKeyMixin):
    """Группы каналов."""

    __tablename__ = "channels_groups"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", name="uq_channels_group_name"),)}

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

    def __repr__(self):
        return f"<ChannelsGroup {self.name}>"


class Channel(Base, UUIDPrimaryKeyMixin):
    """Каналы."""

    __tablename__ = "channels"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", name="uq_channel_name"),)}

    name: Mapped[str | None] = mapped_column(String(30), comment="Название канала")
    description: Mapped[str] = mapped_column(comment="Описание канала")
    channel_group_id: Mapped[uuid.UUID] = mapped_column(
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

    def __repr__(self):
        return f"<Channel {self.name}>"


class Message(Base, BigIntPrimaryKeyMixin):
    """Модель сообщения."""

    __tablename__ = "messages"

    content: Mapped[str] = mapped_column(comment="Содержимое сообщения")
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), comment="Идентификатор канала"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        comment="Идентификатор пользователя",
        default=DELETED_USER_ID,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), comment="Время создания сообщения"
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP, comment="Время последнего изменения сообщения"
    )
    quoted_message_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("messages.id", ondelete="SET DEFAULT"),
        default=DELETED_MESSAGE_ID,
        comment="Идентификатор цитируемого сообщения",
    )

    def __repr__(self):
        return f"<Message {self.id}: {self.content}>"


class LastReadMessageByUser(Base, BigIntPrimaryKeyMixin):
    """Модель хранящее последнее прочитанное сообщение в чате для пользователя."""

    __tablename__ = "last_read_message_by_user"
    __table_args__ = {
        "constraints": (UniqueConstraint("user_id", "channel_id", name="uq_last_read_message_by_user_chanel"),)
    }

    message_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("messages.id", ondelete="CASCADE"), comment="Идентификатор сообщения"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), comment="Идентификатор канала"
    )

    def __repr__(self):
        return f"<LastReadMessageByUser {self.user_id}: {self.channel_id} - {self.message_id}>"
