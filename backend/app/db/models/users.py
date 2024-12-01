import datetime
import uuid

from sqlalchemy import SMALLINT, TIMESTAMP, ForeignKey, String, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import UUIDPrimaryKeyMixin, BigIntPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin):
    """Модель пользователя."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), comment="Почта", unique=True)
    username: Mapped[str] = mapped_column(String(30), comment="Имя пользователя", unique=True)
    hashed_password: Mapped[str] = mapped_column(comment="Хеш пароля")
    phone: Mapped[str] = mapped_column(String(30), comment="Номер телефона")
    first_name: Mapped[str | None] = mapped_column(String(30), comment="Имя")
    second_name: Mapped[str | None] = mapped_column(String(30), comment="Фамилия")
    middle_name: Mapped[str | None] = mapped_column(String(30), comment="Отчество")
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
    """Членство пользователя в компании."""

    __tablename__ = "user_company_membership"
    __table_args__ = {"constraints": (UniqueConstraint("user_id", "company_id", name="uq_user_company"),)}

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
