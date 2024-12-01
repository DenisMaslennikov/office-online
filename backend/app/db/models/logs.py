import uuid

from sqlalchemy import SMALLINT, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import DELETED_USER_ID
from app.db.models.base import Base
from app.db.models.mixins import BigIntPrimaryKeyMixin


class log(Base, BigIntPrimaryKeyMixin):
    """Модель для хранения логов приложения."""

    __tablename__ = "logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET DEFAULT"),
        default=DELETED_USER_ID,
        comment="Идентификатор пользователя создавшего событие",
    )
    event_type_id: Mapped[int] = mapped_column(
        SMALLINT, ForeignKey("event_types.id", ondelete="RESTRICT"), comment="Идентификатор события"
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), comment="Идентификатор организации с которой связано событие"
    )
    old_value: Mapped[str] = mapped_column(comment="Значение до изменения")
    new_value: Mapped[str] = mapped_column(comment="Значение после изменения")
    created_at: Mapped[TIMESTAMP] = mapped_column(server_default=func.now())
    context_type_id: Mapped[SMALLINT] = mapped_column(
        ForeignKey("context_types.id", ondelete="RESTRICT"), comment="Тип контекста события"
    )
    object_id: Mapped[uuid.UUID] = mapped_column(comment="Идентификатор объекта с которым произошло событие")
