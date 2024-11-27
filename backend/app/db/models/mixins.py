from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKey:
    """UUID первичный ключ для моделей алхимии."""

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=uuid4,
        comment="Идентификатор",
    )


class IntPrimaryKey:
    """Целочисленный первичный ключ для моделей алхимии."""

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Идентификатор",
    )
