import datetime
import uuid

from sqlalchemy import SMALLINT, TIMESTAMP, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin):
    """Модель пользователя."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), comment="Почта", unique=True)
    username: Mapped[str] = mapped_column(String(30), comment="Имя пользователя", unique=True)
    hashed_password: Mapped[str] = mapped_column(comment="Хеш пароля")
    phone: Mapped[str | None] = mapped_column(String(30), comment="Номер телефона")
    display_name: Mapped[str] = mapped_column(String(60), comment="Имя для отображения")
    image: Mapped[str | None] = mapped_column(comment="Путь к файлу изображения пользователя", unique=True)
    timezone_id: Mapped[int | None] = mapped_column(
        SMALLINT,
        ForeignKey("timezones.id", ondelete="RESTRICT"),
        comment="Идентификатор таймзоны",
    )
    is_bot: Mapped[bool] = mapped_column(
        comment="Является ли пользователь ботом", server_default=text("false"), default=False
    )
    active: Mapped[bool] = mapped_column(comment="Активен ли аккаунт пользователя", default=True, server_default="true")
    scheduled_deletion_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, comment="Запланированная дата удаления"
    )

    def __repr__(self):
        return f"<User {self.username}({self.email})>"


class UserCompanyMembership(Base, BigIntPrimaryKeyMixin):
    """Членство пользователя в организации."""

    __tablename__ = "user_company_membership"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
        {"comment": "Членство пользователя в организации"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
