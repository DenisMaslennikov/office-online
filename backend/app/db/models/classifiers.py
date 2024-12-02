import uuid

from sqlalchemy import BIGINT, SMALLINT, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DEFAULT_TASK_TYPE_ICON_ID, DELETED_COMPANY_ID
from app.db.models.base import Base
from app.db.models.emuns import icon_category_enum
from app.db.models.mixins import (
    BigIntPrimaryKeyMixin,
    SmallIntPrimaryKeyMixin,
    UUIDPrimaryKeyMixin,
)


class Timezone(Base, SmallIntPrimaryKeyMixin):
    """Классификатор часовых поясов."""

    __tablename__ = "timezones"

    display_name: Mapped[str] = mapped_column(String(30), comment="Отображаемое имя часового пояса")
    iana_name: Mapped[str] = mapped_column(String(256), comment="Наименование IANA часового пояса")

    def __repr__(self):
        return f"<Timezone {self.iana_name}>"


class Role(Base, UUIDPrimaryKeyMixin):
    """Пополняемый классификатор ролей."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("company_id", "name", name="uq_role_company"),
        {"comment": "Классификатор ролей"},
    )

    name: Mapped[str] = mapped_column(String(30), comment="Название роли")
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id"), comment="Идентификатор компании управляющей ролью"
    )

    def __repr__(self):
        return f"<Role {self.company_id} - {self.name}>"


# class GlobalPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
#     """Классификатор глобальных возможных разрешений."""
#
#     __tablename__ = "global_permissions"
#
#
# class ProjectPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
#     """Классификатор возможных разрешений для проекта."""
#
#     __tablename__ = "project_permissions"
#
#
# class FileGroupPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
#     """Классификатор возможных разрешений для группы файлов."""
#
#     __tablename__ = "file_group_permissions"
#
#
# class ChannelPermission(Base, SmallIntPrimaryKeyMixin, PermissionClassifierMixin):
#     """Классификатор возможных разрешений для каналов чата."""
#
#     __tablename__ = "channels_permissions"


class TaskType(Base, BigIntPrimaryKeyMixin):
    """Пополняемый классификатор типов задач."""

    __tablename__ = "task_types"
    __table_args__ = (
        UniqueConstraint("name", "company_id", name="uq_task_type_name_for_company"),
        UniqueConstraint("name", "project_id", name="uq_task_type_name_for_project"),
        CheckConstraint(
            "(company_id IS NOT NULL AND project_id IS NULL) OR (company_id IS NULL AND project_id IS NOT NULL)",
            name="chk_company_or_project",
        ),
        {"comment": "Пополняемый классификатор типов задач"},
    )

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

    def __repr__(self):
        return f"<TaskType {self.name}>"


class Icon(Base, BigIntPrimaryKeyMixin):
    """Пополняемый классификатор для хранения ссылок на иконки."""

    __tablename__ = "icons"

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET DEFAULT"),
        comment="Идентификатор организации",
        default=DELETED_COMPANY_ID,
    )
    file_name: Mapped[str] = mapped_column(comment="Имя файла", unique=True)
    icon_category_id: Mapped[str] = mapped_column(icon_category_enum, comment="Категория иконок")

    def __repr__(self):
        return f"<Icon {self.company_id} - {self.file_name}>"


# class IconCategory(Base, SmallIntPrimaryKeyMixin):
#     """Модель классификатора категорий иконок."""
#
#     __tablename__ = "icons_categories"
#
#     name: Mapped[str] = mapped_column(String(100), comment="Наименование категории иконок")
#     description: Mapped[str] = mapped_column(comment="Описание категории иконок")
#
#     def __repr__(self):
#         return f"<IconCategory {self.name}>"


# class FileGroupType(Base, SmallIntPrimaryKeyMixin):
#     """Классификатор типов групп."""
#
#     __tablename__ = "file_group_types"
#
#     display_name: Mapped[str] = mapped_column(String(100), comment="Наименование группы файлов", unique=True)
#     system_name: Mapped[str] = mapped_column(String(100), comment="Системное имя типа группы файлов", unique=True)
#     can_change_permissions: Mapped[bool] = mapped_column(comment="Можно ли у группы менять права")
#     can_delete: Mapped[bool] = mapped_column(comment="Можно ли удалять группу")
#     trash: Mapped[bool] = mapped_column(comment="Признак того что группа является корзиной")
#
#     def __repr__(self):
#         return f"<FileGroupType {self.system_name}>"


# class FileGroupTypeDefaultPermission(Base, SmallIntPrimaryKeyMixin):
#     """Настройки прав по умолчанию для типов групп файлов."""
#
#     __tablename__ = "file_group_type_default_permissions"
#
#     role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), comment="Идентификатор роли")
#     file_group_type_id: Mapped[int] = mapped_column(
#         SMALLINT, ForeignKey("file_group_types.id", ondelete="CASCADE"), comment="Идентификатор типа группы файлов"
#     )
#     file_group_permission_id: Mapped[int] = mapped_column(
#         SMALLINT, ForeignKey("file_group_permissions.id", ondelete="CASCADE"), comment="Идентификатор разрешения"
#     )
#
#     def __repr__(self):
#         return (
#             f"<FileGroupTypeDefaultPermission {self.role_id}: {self.file_group_type_id} - "
#             f"{self.file_group_permission_id}>"
#         )


class EventType(Base, SmallIntPrimaryKeyMixin):
    """Классификатор событий для записи в логе."""

    __tablename__ = "event_types"

    system_name: Mapped[str] = mapped_column(String(20), unique=True, comment="Системное название события")
    event_display_string: Mapped[str] = mapped_column(String(255), comment="Строка для вывода события")

    def __repr__(self):
        return f"<EventType {self.system_name}>"


class ContextType(Base, SmallIntPrimaryKeyMixin):
    """Классификатор типа контекста."""

    __tablename__ = "context_types"

    system_name: Mapped[str] = mapped_column(String(20), comment="Системное имя контекста")
    display_name: Mapped[str] = mapped_column(String(20), comment="Имя контекста для отображения пользователю")

    def __repr__(self):
        return f"<ContextType {self.system_name}>"


# class SubjectType(Base, SmallIntPrimaryKeyMixin):
#     """Классификатор типов субъектов."""
#
#     __tablename__ = "subject_types"
#
#     system_name: Mapped[str] = mapped_column(String(20), comment="Системное имя типа субъекта")
#     display_name: Mapped[str] = mapped_column(String(20), comment="Имя типа субъекта для отображения пользователю")
#
#     def __repr__(self):
#         return f"<SubjectType {self.system_name}>"


class Permission(Base, SmallIntPrimaryKeyMixin):
    """Классификатор возможных прав."""

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("display_name", "context_type_id", name="uq_display_name_context_type"),
        {"comment": "Классификатор возможных прав"},
    )

    context_type_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("context_types.id", ondelete="RESTRICT"), comment="Идентификатор типа контекста"
    )
    system_name: Mapped[str] = mapped_column(String(20), comment="Системное имя разрешения", unique=True)
    display_name: Mapped[str] = mapped_column(String(50), comment="Имя разрешения для пользователя")

    def __repr__(self):
        return f"<Permission {self.display_name}>"
