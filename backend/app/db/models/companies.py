import datetime

from sqlalchemy import SMALLINT, TIMESTAMP, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin


class Company(Base, UUIDPrimaryKeyMixin):
    """Модель компании."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(comment="Наименование организации")
    description: Mapped[str | None] = mapped_column(comment="Описание организации")
    subdomain: Mapped[str] = mapped_column(String(50), comment="Субдомен организации", unique=True)
    timezone_id: Mapped[int] = mapped_column(
        SMALLINT,
        ForeignKey("timezones.id", ondelete="RESTRICT"),
        comment="Идентификатор таймзоны",
    )
    logo: Mapped[str | None] = mapped_column(comment="Логотип организации")
    scheduled_deletion_date: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP, comment="Дата запланированного удаления компании"
    )
    active: Mapped[bool] = mapped_column(comment="Компания активна", default=True, server_default=text("true"))

    def __repr__(self):
        return f"<Company {self.name}>"
