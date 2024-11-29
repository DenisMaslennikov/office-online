import uuid

from sqlalchemy import String, ForeignKey, SMALLINT, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import LtreeType

from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin, UUIDPrimaryKeyMixin


class ChannelsGroup(Base, BigIntPrimaryKeyMixin):
    """Группы каналов."""

    __tablename__ = "channels_groups"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", name="uq_channels_group_name"),)}

    name: Mapped[str] = mapped_column(String(30), comment="Имя группы")
    description: Mapped[str] = mapped_column(comment="Описание группы")
    path: Mapped[LtreeType] = mapped_column(LtreeType, comment="Иерархия группы")
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    system: Mapped[bool] = mapped_column(comment="Является системной")
    order: Mapped[int] = mapped_column(SMALLINT, comment="Порядок при сортировке")


class Channel(Base, UUIDPrimaryKeyMixin):
    """Каналы."""

    __tablename__ = "channels"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", name="uq_channel_name"),)}

    name: Mapped[str | None] = mapped_column(String(30), comment="Название канала")
    description: Mapped[str] = mapped_column(comment="Описание канала")
    chanel_group_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("channels_groups.id", ondelete="CASCADE"), comment="Идентификатор группы каналов"
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор компании"
    )
    order: Mapped[int] = mapped_column(SMALLINT, comment="Порядок при сортировке")
    system: Mapped[bool] = mapped_column(comment="Системный канал")
    private: Mapped[bool] = mapped_column(comment="Приватный чат")
