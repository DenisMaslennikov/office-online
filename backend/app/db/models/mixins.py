from uuid import UUID, uuid4

from sqlalchemy import text, BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKey:
    """UUID первичный ключ для моделей алхимии."""

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        default=uuid4,
        comment="Идентификатор",
    )


class BigIntPrimaryKey:
    """Большой целочисленный первичный ключ для моделей алхимии."""

    id: Mapped[int] = mapped_column(
        BIGINT,
        primary_key=True,
        comment="Идентификатор",
    )


class SmallIntPrimaryKey:
    """Маленький целочисленный первичный ключ для моделей алхимии."""

    id: Mapped[int] = mapped_column(
        SMALLINT,
        primary_key=True,
        comment="Идентификатор",
    )
