import uuid

from sqlalchemy import SMALLINT, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base
from app.db.models.enums import subject_type_enum
from app.db.models.mixins import BigIntPrimaryKeyMixin


class CompanyUserRole(Base, BigIntPrimaryKeyMixin):
    """Роли пользователей в компании."""

    __tablename__ = "company_users_roles"
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", "role_id", name="uq_company_user_role"),
        {"comment": "Роли пользователей в компании"},
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), comment="Идентификатор пользователя"
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        comment="Идентификатор роли",
    )

    def __repr__(self):
        return f"<CompanyUserRole {self.company_id}: ({self.user_id}) - {self.role_id}>"


class SubjectPermissionToObject(Base, BigIntPrimaryKeyMixin):
    """Права субъекта на объект."""

    __tablename__ = "subject_permissions_to_object"

    __table_args__ = (
        UniqueConstraint("permission_id", "subject_id", "object_id", name="uq_subject_permission_to_object"),
        {"comment": "Права субъекта на объект"},
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(comment="Идентификатор субъекта (роли или пользователя)")
    subject_type: Mapped[str] = mapped_column(subject_type_enum, comment="Тип субъекта")
    permission_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("permissions.id", ondelete="RESTRICT"), comment="Идентификатор разрешения"
    )
    object_id: Mapped[uuid.UUID] = mapped_column(comment="Идентификатор объекта на который действует разрешение")

    def __repr__(self):
        return (
            f"<SubjectPermissionToObject {self.subject_type_id} - {self.subject_id}: ({self.permission_id}) - "
            f"{self.object_id}>"
        )
