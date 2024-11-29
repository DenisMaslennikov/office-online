import uuid

from sqlalchemy import String, ForeignKey, SMALLINT, UniqueConstraint
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


class Channels(Base, UUIDPrimaryKeyMixin):
    """Каналы."""

    __tablename__ = "channels"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", name="uq_channel_name"),)}
