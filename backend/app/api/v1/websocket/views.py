from uuid import UUID, uuid4

import orjson
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.logger import logger
from app.rabbitmq import rabbitmq_client
from app.db.models.mixins import UUIDPrimaryKeyMixin

router = APIRouter(tags=["websocket"])

company_id = UUID("e7682ea1-d0fd-44e1-9760-5d2f6b83e969")
chanel_id = UUID("a56fef68-33cd-4173-917b-e74365a5cdb8")


@router.websocket("/chat/")
async def chat_websocket(websocket: WebSocket):
    logger.debug("Новое подключение к websocket")
    await websocket.accept()
    user_id = uuid4()
    await rabbitmq_client.update_channels_bindings(company_id, chanel_id, user_id, "add")
    while True:
        try:
            message = await websocket.receive_json()
            logger.debug(f"Получено сообщение от {user_id} message: {message}")
            await rabbitmq_client.publish(company_id, chanel_id, orjson.dumps(message))
        except WebSocketDisconnect:
            logger.debug(f"Клиент {user_id} отключился")
            await rabbitmq_client.delete_queue(user_id)
            break
