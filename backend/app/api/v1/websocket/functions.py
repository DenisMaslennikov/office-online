from starlette.websockets import WebSocket

from app import logger


async def rabbitmq_message_handler(message: str, websocket: WebSocket):
    """Обработка сообщения из RabbitMQ."""
    logger.debug(f"Получено сообщение из RabbitMQ {message}")
    await websocket.send_text(message)
