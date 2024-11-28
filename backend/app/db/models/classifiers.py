import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import (
    SmallIntPrimaryKeyMixin,
    UUIDPrimaryKeyMixin,
    PermissionClassifierMixin,
    BigIntPrimaryKeyMixin,
)


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


class GlobalPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
    """Классификатор глобальных возможных разрешений."""

    __tablename__ = "global_permissions"


class ProjectPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
    """Классификатор возможных разрешений для проекта."""

    __tablename__ = "project_permissions"


class TaskType(Base, BigIntPrimaryKeyMixin):
    """Пополняемый классификатор типов задач."""

    __tablename__ = "task_types"
    __table_args__ = {"constraints": (UniqueConstraint("name", "company_id", "project_id", name="uq_task_type_name"),)}

    name: Mapped[str] = mapped_column(String(100), comment="Наименование типа задачи")
    description: Mapped[str] = mapped_column(comment="Описание типа задачи")
    icon_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("icons.id", ondelete="RESTRICT"), comment="Идентификатор иконки"
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )
