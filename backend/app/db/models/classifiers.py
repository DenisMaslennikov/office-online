import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint, BIGINT, SMALLINT, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DELETED_COMPANY_ID, DEFAULT_TASK_TYPE_ICON_ID
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


class FileGroupPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
    """Классификатор возможных разрешений для группы файлов."""

    __tablename__ = "file_group_permissions"


class TaskType(Base, BigIntPrimaryKeyMixin):
    """Пополняемый классификатор типов задач."""

    __tablename__ = "task_types"
    __table_args__ = {
        "constraints": (
            UniqueConstraint("name", "company_id", name="uq_task_type_name_for_company"),
            UniqueConstraint("name", "project_id", name="uq_task_type_name_for_project"),
            CheckConstraint(
                "(company_id IS NOT NULL AND project_id IS NULL) OR (company_id IS NULL AND project_id IS NOT NULL)",
                name="chk_company_or_project",
            ),
        ),
    }

    name: Mapped[str] = mapped_column(String(100), comment="Наименование типа задачи")
    description: Mapped[str] = mapped_column(comment="Описание типа задачи")
    icon_id: Mapped[int] = mapped_column(
        BIGINT,
        ForeignKey("icons.id", ondelete="SET DEFAULT"),
        comment="Идентификатор иконки",
        default=DEFAULT_TASK_TYPE_ICON_ID,
    )
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), comment="Идентификатор проекта"
    )


class Icon(Base, BigIntPrimaryKeyMixin):
    """Пополняемый классификатор для хранения ссылок на иконки."""

    __tablename__ = "icons"

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET DEFAULT"),
        comment="Идентификатор организации",
        default=DELETED_COMPANY_ID,
    )
    file_name: Mapped[str] = mapped_column(comment="Имя файла", unique=True)
    icon_category_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("icons_categories.id"), comment="Идентификатор категории иконок"
    )


class IconCategory(Base, SmallIntPrimaryKeyMixin):
    """Модель классификатора категорий иконок."""

    __tablename__ = "icons_categories"

    name: Mapped[str] = mapped_column(String(100), comment="Наименование категории иконок")
    description: Mapped[str] = mapped_column(comment="Описание категории иконок")


class FileGroupType(Base, SmallIntPrimaryKeyMixin):
    """Классификатор типов групп."""

    __tablename__ = "file_group_types"

    display_name: Mapped[str] = mapped_column(String(100), comment="Наименование группы файлов", unique=True)
    system_name: Mapped[str] = mapped_column(String(100), comment="Системное имя типа группы файлов", unique=True)
    system: Mapped[bool] = mapped_column(comment="Системная группа (нельзя менять права по умолчанию)")
    trash: Mapped[bool] = mapped_column(comment="Признак того что группа является корзиной")


class FileGroupTypeDefaultPermission(Base, SmallIntPrimaryKeyMixin):
    """Настройки прав по умолчанию для типов групп файлов."""

    __tablename__ = "file_group_type_default_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), comment="Идентификатор роли")
    file_group_type_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("file_group_types.id", ondelete="CASCADE"), comment="Идентификатор типа группы файлов"
    )
    file_group_permission_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("file_group_permissions.id", ondelete="CASCADE"), comment="Идентификатор разрешения"
    )
