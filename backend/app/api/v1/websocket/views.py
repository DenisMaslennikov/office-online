import asyncio
from pprint import pprint
from uuid import UUID, uuid4

import orjson
from dns.asyncresolver import try_ddr
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from app.config import settings
from app.logger import logger
from app.rabbitmq import rabbitmq_client

router = APIRouter(tags=["websocket"])

company_id = UUID("e7682ea1-d0fd-44e1-9760-5d2f6b83e969")
chanel_id = UUID("a56fef68-33cd-4173-917b-e74365a5cdb8")


async def rabbitmq_message_handler(message: str, websocket: WebSocket):
    """Обработка сообщения из RabbitMQ."""
    logger.debug(f"Получено сообщение из RabbitMQ {message}")
    await websocket.send_text(message)


@router.websocket("/chat/")
async def chat_websocket(websocket: WebSocket) -> None:
    """Метод для обслуживания вебсокет подключения к чату."""
    logger.debug("Новое подключение к websocket")
    await websocket.accept()
    user_id = uuid4()

    async def consume_queue() -> None:
        """Получение сообщения из RabbitMQ."""
        await rabbitmq_client.consume(user_id, lambda message: rabbitmq_message_handler(message, websocket))

    await rabbitmq_client.update_channels_bindings(company_id, chanel_id, user_id, "add")

    consume_queue_task = asyncio.create_task(consume_queue())
    try:
        while True:
            message = await websocket.receive_text()
            if len(message.encode("utf-8")) > settings.max_websocket_message_size:
                await websocket.close(code=1009, reason="Слишком большое сообщение")
                break
            try:
                message_json = orjson.loads(message)
                pprint(message_json)
            except orjson.JSONDecodeError as e:
                logger.error(f"Ошибка декодирования json для сообщения {message}", exc_info=e)
                await websocket.close(code=1003, reason="Полученное сообщение не является json")
                break

            logger.debug(f"Получено сообщение от {user_id} message: {message}")
            await rabbitmq_client.publish(company_id, chanel_id, message.encode("utf-8"))
    except WebSocketDisconnect:
        logger.debug(f"Клиент {user_id} отключился")
    finally:
        consume_queue_task.cancel()
        await rabbitmq_client.delete_queue(user_id)
