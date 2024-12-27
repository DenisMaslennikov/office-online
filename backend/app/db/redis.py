import uuid
from typing import Type, Any

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis

from app.config import settings

redis_client = Redis(host=settings.redis.host, port=settings.redis.port, decode_responses=True)


async def update_object_cache(prefix: str, schema: BaseModel) -> None:
    """Обновляет кеш redis."""
    await redis_client.set(f"{prefix}:{schema.id}", schema.model_dump_json(), ex=get_ttl_by_prefix(prefix))


async def get_object_from_cache(prefix: str, id: str | uuid.UUID | int, model: Type[BaseModel]) -> BaseModel | None:
    """Получение объекта из кеша Redis."""
    redis_data = await redis_client.get(f"{prefix}:{id}")
    if redis_data is None:
        return None
    data = orjson.loads(redis_data)
    if isinstance(data["id"], str) and len(data["id"]) == 36:  # Длина uuid
        data["id"] = uuid.UUID(data["id"])
    return model(**data)


async def get_raw_data_from_cache(prefix: str, id: str | uuid.UUID | int) -> Any:
    """Получение сырых данных из кеша Redis."""
    redis_data = await redis_client.get(f"{prefix}:{id}")
    if redis_data is None:
        return None
    return orjson.loads(redis_data)


async def update_raw_data_cache(prefix: str, key: Any, value: Any) -> None:
    """Записывает сырые данные по ключу с префиксом."""
    await redis_client.set(f"{prefix}:{key}", orjson.dumps(value), ex=get_ttl_by_prefix(prefix))



async def delete_from_cache(prefix: str, id: str | uuid.UUID | int) -> None:
    """Удаляет значение из кеша Redis."""
    await redis_client.delete(f"{prefix}:{id}")


def get_ttl_by_prefix(prefix: str) -> int | None:
    """Получение времени жизни по префиксу."""
    return settings.redis.ttl_override.get(prefix) or settings.redis.default_ttl
