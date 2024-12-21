import datetime
import uuid
from typing import TYPE_CHECKING

import bcrypt
from sqlalchemy import SMALLINT, TIMESTAMP, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.db.models import Timezone


class User(Base, UUIDPrimaryKeyMixin):
    """Модель пользователя."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), comment="Почта", unique=True)
    username: Mapped[str] = mapped_column(String(30), comment="Имя пользователя", unique=True)
    hashed_password: Mapped[str | None] = mapped_column(comment="Хеш пароля")
    phone: Mapped[str | None] = mapped_column(String(30), comment="Номер телефона")
    display_name: Mapped[str | None] = mapped_column(String(60), comment="Имя для отображения")
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
    scheduled_deletion_date: Mapped[datetime.datetime | None] = mapped_column(
        TIMESTAMP, comment="Запланированная дата удаления"
    )

    timezone: Mapped["Timezone"] = relationship()

    def __repr__(self):
        return f"<User {self.username}({self.email})>"

    @hybrid_property
    def password(self):
        """Hybrid property для пароля."""
        raise AttributeError("Атрибут пароль нельзя читать напрямую.")

    @password.setter
    def password(self, plain_password: str) -> None:
        """Сеттер пароля."""
        self.hashed_password = self._generate_password_hash(plain_password)

    def _generate_password_hash(self, plain_password: str) -> str:
        """Генерация хеша пароля с использованием bcrypt."""
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str) -> bool:
        """Проверка пароля через сравнение хеша."""
        return bcrypt.checkpw(plain_password.encode("utf-8"), self.hashed_password.encode("utf-8"))


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
