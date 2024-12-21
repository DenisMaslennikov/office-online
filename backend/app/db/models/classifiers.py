import uuid

from sqlalchemy import BIGINT, SMALLINT, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DEFAULT_TASK_TYPE_ICON_ID, DELETED_COMPANY_ID
from app.db.models.base import Base
from app.db.models.enums import icon_category_enum
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
    icon_category: Mapped[str] = mapped_column(icon_category_enum, comment="Категория иконок")

    def __repr__(self):
        return f"<Icon {self.company_id} - {self.file_name}>"


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


class ProjectType(Base, SmallIntPrimaryKeyMixin):
    """Классификатор типов проектов."""

    __tablename__ = "project_types"

    name: Mapped[str] = mapped_column(String(30), comment="Название типа проекта")

    def __repr__(self):
        return f"<ProjectType {self.name}>"


class TaskLinkType(Base, SmallIntPrimaryKeyMixin):
    """Классификатор типов связи задач."""

    __tablename__ = "task_link_types"

    status: Mapped[str] = mapped_column(String(30), comment="Статус")
    invert_status: Mapped[bool] = mapped_column(String(30), comment="Обратный статус")

    def __repr__(self):
        return f"<TaskLinkType {self.status} - {self.invert_status}>"


class Smile(Base, BigIntPrimaryKeyMixin):
    """Модель для хранения смайлов."""

    __tablename__ = "smiles"

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор компании"
    )
    code: Mapped[str] = mapped_column(String(30), comment="Код смайлика")
    filename: Mapped[str] = mapped_column(comment="Имя файла")
