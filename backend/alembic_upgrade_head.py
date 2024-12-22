from alembic import command
from alembic.config import Config as AlembicConfig

from app import settings

# Запустить миграции Alembic
alembic_cfg = AlembicConfig("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", settings.db.database_uri)

command.upgrade(alembic_cfg, "head")
