import asyncio
from functools import partial
from typing import Annotated
from uuid import UUID, uuid4

import orjson
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.params import Query

from app.api.v1.websocket.functions import rabbitmq_message_handler
from app.config import settings
from app.constants import RabbitMQRoutingKeysTypes
from app.logger import logger
from app.rabbitmq import rabbitmq_client

router = APIRouter(tags=["websocket"])

company_id = UUID("e7682ea1-d0fd-44e1-9760-5d2f6b83e969")
channel_id = UUID("a56fef68-33cd-4173-917b-e74365a5cdb8")


@router.websocket("/chat/")
async def chat_websocket(websocket: WebSocket, token: Annotated[str, Query(title="access JWT токен")]) -> None:
    """Метод для обслуживания вебсокет подключения к чату."""
    logger.debug("Новое подключение к websocket")
    await websocket.accept()
    # TODO Убрать при подключении базы
    user_id = uuid4()

    async def consume_queue() -> None:
        """Получение сообщения из RabbitMQ."""
        await rabbitmq_client.consume(user_id, partial(rabbitmq_message_handler, websocket=websocket))

    await rabbitmq_client.update_channels_bindings(
        company_id=company_id,
        channel_id=channel_id,
        user_id=user_id,
        type=RabbitMQRoutingKeysTypes.MESSAGES,
        action="add",
    )

    consume_queue_task = asyncio.create_task(consume_queue())
    try:
        while True:
            message = await websocket.receive_text()
            if len(message.encode("utf-8")) > settings.websocket.max_websocket_message_size:
                await websocket.close(code=1009, reason="Слишком большое сообщение")
                break
            try:
                message_json = orjson.loads(message)
            except orjson.JSONDecodeError as e:
                logger.error(f"Ошибка декодирования json для сообщения {message}", exc_info=e)
                await websocket.close(code=1003, reason="Полученное сообщение не является json")
                break

            logger.debug(f"Получено сообщение от {user_id} message: {message}")
            await rabbitmq_client.publish(
                company_id=company_id,
                channel_id=channel_id,
                type=RabbitMQRoutingKeysTypes.MESSAGES,
                message=message.encode("utf-8"),
            )
    except WebSocketDisconnect:
        logger.debug(f"Клиент {user_id} отключился")
    finally:
        consume_queue_task.cancel()
        await rabbitmq_client.delete_queue(user_id)
