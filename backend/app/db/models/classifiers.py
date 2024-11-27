from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import Base
from app.db.models.mixins import SmallIntPrimaryKey


class Timezones(Base, SmallIntPrimaryKey):
    """Классификатор часовых поясов."""

    __tablename__ = "timezones"

    display_name: Mapped[str] = mapped_column(String(30), comment="Отображаемое имя часового пояса")
    iana_name: Mapped[str] = mapped_column(String(256), comment="Наименование IANA часового пояса")
