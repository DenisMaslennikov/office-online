import uuid

from sqlalchemy import ForeignKey, SMALLINT, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin


class SubjectPermissionCompany(Base, BigIntPrimaryKeyMixin):
    """Разрешения для роли или пользователя в компании."""

    __tablename__ = "subject_permissions_company"

    __table_args__ = {
        "constraints": (
            UniqueConstraint("role_id", "global_permission_id", "company_id", name="uq_role_permissions_company"),
            UniqueConstraint("user_id", "global_permission_id", "company_id", name="uq_user_permissions_company"),
            CheckConstraint(
                "(role_id IS NOT NULL AND user_id IS NULL) OR (role_id IS NULL AND user_id IS NOT NULL)",
                name="chk_role_or_user",
            ),
        )
    }

    role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), comment="Идентификатор роли"
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    global_permission_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("global_permissions.id", ondelete="CASCADE"), comment="Идентификатор разрешения"
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )


class CompanyUserRole(Base, BigIntPrimaryKeyMixin):
    """Роли пользователей в компании."""

    __tablename__ = "company_users_roles"
    __table_args__ = {
        "constraints": (UniqueConstraint("company_id", "user_id", "role_id", name="uq_company_user_role"),)
    }

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), comment="Идентификатор роли")


class SubjectPermissionProject(Base, BigIntPrimaryKeyMixin):
    """Права роли или пользователя на проекте."""

    __tablename__ = "subject_permissions_project"
    __table_args__ = {
        "constraints": (
            UniqueConstraint("project_id", "role_id", "project_permission_id", name="uq_role_permissions_project"),
            UniqueConstraint("project_id", "user_id", "project_permission_id", name="uq_user_permissions_project"),
            CheckConstraint(
                "(role_id IS NOT NULL AND user_id IS NULL) OR (role_id IS NULL AND user_id IS NOT NULL)",
                name="chk_role_or_user",
            ),
        )
    }

    role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), comment="Идентификатор роли"
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    project_permission_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("project_permissions.id", ondelete="RESTRICT", comment="Идентификатор разрешения")
    )


class SubjectPermissionFileGroup(Base, BigIntPrimaryKeyMixin):
    """Права на группу файлов."""

    __tablename__ = "subject_permissions_files_group"
    __table_args__ = {
        "constraints": (
            UniqueConstraint(
                "file_group_id", "role_id", "file_group_permission_id", name="uq_role_file_group_permission"
            ),
            UniqueConstraint(
                "file_group_id", "user_id", "file_group_permission_id", name="uq_user_file_group_permission"
            ),
            CheckConstraint(
                "(role_id IS NOT NULL AND user_id IS NULL) OR (role_id IS NULL AND user_id IS NOT NULL)",
                name="chk_role_or_user",
            ),
        )
    }

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), comment="Идентификатор роли"
    )
    file_group_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("file_groups.id", ondelete="CASCADE"), comment="Идентификатор группы файлов"
    )
    file_group_permission_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("file_group_permissions.id", ondelete="RESTRICT"), comment="Идентификатор разрешения"
    )
