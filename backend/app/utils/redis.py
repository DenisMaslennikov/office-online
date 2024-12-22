import uuid
from pprint import pprint
from typing import Type

from redis.asyncio import Redis
from pydantic import BaseModel
import orjson

from app.config import settings

redis_client = Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True)


async def update_cash(prefix: str, schema: BaseModel) -> None:
    """Обновляет кеш redis."""
    await redis_client.set(f"{prefix}:{schema.id}", schema.model_dump_json())


async def get_from_cash(prefix: str, id: str | uuid.UUID | int, model: Type[BaseModel]) -> BaseModel:
    """Получение объекта из кеша Redis."""
    data = orjson.loads(await redis_client.get(f"{prefix}:{id}"))
    if len(data["id"]) == 36:
        data["id"] = uuid.UUID(data["id"])
    return model(**data)
