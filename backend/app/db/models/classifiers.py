import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import SmallIntPrimaryKeyMixin, UUIDPrimaryKeyMixin


class Timezones(Base, SmallIntPrimaryKeyMixin):
    """Классификатор часовых поясов."""

    __tablename__ = "timezones"

    display_name: Mapped[str] = mapped_column(String(30), comment="Отображаемое имя часового пояса")
    iana_name: Mapped[str] = mapped_column(String(256), comment="Наименование IANA часового пояса")


class Roles(Base, UUIDPrimaryKeyMixin):
    """Пополняемый классификатор ролей."""

    __tablename__ = "roles"
    __table_args__ = {"constraints": (UniqueConstraint("company_id", "name", name="uq_role_company"),)}

    name: Mapped[str] = mapped_column(String(30), comment="Название роли")
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id"), comment="Идентификатор компании управляющей ролью"
    )


class GlobalPermission(Base, SmallIntPrimaryKeyMixin):
    """Классификатор глобальных возможных разрешений."""

    __tablename__ = "global_permissions"

    display_name: Mapped[str] = mapped_column(
        String(100), unique=True, comment="Имя разрешения для отображения пользователям"
    )
    system_name: Mapped[str] = mapped_column(String(100), unique=True, comment="Системное имя разрешения")
    description: Mapped[str | None] = mapped_column(comment="Описание разрешения")
