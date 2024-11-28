from sqlalchemy import String, SMALLINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import UUIDPrimaryKeyMixin
from app.db.models.base import Base


class Company(Base, UUIDPrimaryKeyMixin):
    """Модель компании."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(comment="Наименование организации")
    description: Mapped[str | None] = mapped_column(comment="Описание организации")
    subdomain: Mapped[str] = mapped_column(String(50), comment="Субдомен организации")
    timezone_id: Mapped[int] = mapped_column(
        SMALLINT,
        ForeignKey("timezones.id", ondelete="RESTRICT"),
        comment="Идентификатор таймзоны",
    )
    logo: Mapped[str | None] = mapped_column(comment="Логотип организации")

    def __repr__(self):
        return self.name
