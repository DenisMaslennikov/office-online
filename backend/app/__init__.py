from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.config import settings
from app.db import db_helper
from app.logger import logger
from app.rabbitmq import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Жизненный цикл приложения."""
    logger.debug("Инициализация FastAPI приложения")
    await rabbitmq_client.connect()

    yield

    logger.debug("Закрытие FasAPI приложения")
    await db_helper.dispose()
    await rabbitmq_client.close()


main_app = FastAPI(lifespan=lifespan)

main_app.include_router(api_router, prefix=settings.api.prefix)
