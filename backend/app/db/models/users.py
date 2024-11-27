from sqlalchemy import String, SMALLINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.mixins import UUIDPrimaryKey
from app.db.models.base import Base


class User(Base, UUIDPrimaryKey):
    """Модель пользователя"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), comment="Почта", unique=True)
    username: Mapped[str] = mapped_column(String(30), comment="Имя пользователя", unique=True)
    hashed_password: Mapped[str] = mapped_column(comment="Хеш пароля")
    first_name: Mapped[str] = mapped_column(String(30), comment="Имя")
    second_name: Mapped[str] = mapped_column(String(30), comment="Фамилия")
    middle_name: Mapped[str] = mapped_column(String(30), comment="Отчество")
    image: Mapped[str] = mapped_column(comment="Путь к файлу изображения пользователя", unique=True)
    timezone_id: Mapped[int] = mapped_column(
        SMALLINT,
        ForeignKey("timezones.id", ondelete="RESTRICT"),
        comment="Идентификатор таймзоны",
    )
    is_bot: Mapped[bool] = mapped_column(comment="Является ли пользователь ботом")
    active: Mapped[bool] = mapped_column(comment="Активен ли аккаунт пользователя")

    def __repr__(self):
        return self.username
