import uuid
from typing import Type

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis

from app.config import settings

redis_client = Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True)


async def update_cache(prefix: str, schema: BaseModel, ttl: int | None = None) -> None:
    """Обновляет кеш redis."""
    await redis_client.set(f"{prefix}:{schema.id}", schema.model_dump_json(), ex=ttl)


async def get_from_cache(prefix: str, id: str | uuid.UUID | int, model: Type[BaseModel]) -> BaseModel | None:
    """Получение объекта из кеша Redis."""
    redis_data = await redis_client.get(f"{prefix}:{id}")
    if redis_data is None:
        return None
    data = orjson.loads(redis_data)
    if len(data["id"]) == 36:
        data["id"] = uuid.UUID(data["id"])
    return model(**data)


async def delete_from_cache(prefix: str, id: str | uuid.UUID | int) -> None:
    """Удаляет значение из кеша Redis."""
    await redis_client.delete(f"{prefix}:{id}")
