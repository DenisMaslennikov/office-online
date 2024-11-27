import uvicorn
from alembic import command
from alembic.config import Config as AlembicConfig

from app import main_app
from app.config import settings

__all__ = ["main_app"]

if __name__ == "__main__":
    alembic_cfg = AlembicConfig("alembic.ini")

    alembic_cfg.set_main_option("sqlalchemy.url", settings.db.database_uri)

    command.upgrade(alembic_cfg, "head")

    # Запуск сервера
    uvicorn.run("run:main_app", host="0.0.0.0", port=8000, reload=settings.reload)
