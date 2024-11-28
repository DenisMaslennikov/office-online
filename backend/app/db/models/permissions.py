import uuid

from sqlalchemy import ForeignKey, SMALLINT, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKey


class SubjectPermissionCompany(Base, BigIntPrimaryKey):
    """Разрешения для роли или пользователя в компании."""

    __tablename__ = "subject_permissions_company"

    __table_args__ = {
        "constraints": (
            UniqueConstraint(
                "role_id", "user_id", "global_permission_id", "company_id", name="uq_subject_permissions_company"
            ),
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


class CompanyUserRole(Base, BigIntPrimaryKey):
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
