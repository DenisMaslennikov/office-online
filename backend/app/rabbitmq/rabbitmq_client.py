from typing import Awaitable, Callable
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractExchange, AbstractQueue

from app.config import settings
from app.logger import logger


class AIORabbiMQClient:
    """Ассинхронный клиент для RabbitMQ."""

    def __init__(
        self,
        host: str = settings.rabbitmq.host,
        port: int = settings.rabbitmq.port,
        login: str = settings.rabbitmq.user,
        password: str = settings.rabbitmq.password,
    ):
        """Настройки подключения."""
        logger.debug("Инициализация RabbitMQ клиента")
        self.host: str = host
        self.port: int = port
        self.login: str = login
        self.password: str = password
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.Channel | None = None
        self.exchanges: dict[str, AbstractExchange] = {}

    async def connect(self) -> None:
        """Подключение к серверу RabbitMQ."""
        logger.debug("Подключение к RabbitMQ...")
        self.connection = await aio_pika.connect_robust(
            host=self.host, port=self.port, login=self.login, password=self.password
        )
        self.channel = await self.connection.channel()

    async def _declare_exchange(
        self,
        exchange_name: str,
        exchange_type: str = aio_pika.ExchangeType.TOPIC,
        durable: bool = False,
        auto_delete: bool = False,
    ) -> AbstractExchange:
        """Создает обменник с заданными параметрами."""
        logger.debug(f"Создаю обменник {exchange_name}")
        self.exchanges[exchange_name] = await self.channel.declare_exchange(
            exchange_name,
            exchange_type,
            durable=durable,
            auto_delete=auto_delete,
        )
        return self.exchanges[exchange_name]

    async def publish(self, company_id: UUID, channel_id: UUID, message: bytes) -> None:
        """Публикует сообщение в обменник."""
        exchange_name = settings.rabbitmq.exchange_name_template.format(company_id=company_id)
        routing_key = settings.rabbitmq.routing_key_template.format(channel_id=channel_id)
        try:
            exchange = self.exchanges.get(exchange_name)
            if exchange is None:
                exchange = await self._declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, auto_delete=True)
            logger.debug(f"Публикую сообщение в {exchange_name}: {message}")
            await exchange.publish(aio_pika.Message(message), routing_key=routing_key)
        except aio_pika.exceptions.ChannelClosed:
            logger.debug("Обменник был удален. Создаю новый обменник.")
            exchange = await self._declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, auto_delete=True)
            await exchange.publish(aio_pika.Message(message), routing_key=routing_key)

    async def update_channels_bindings(self, company_id: UUID, channel_id: UUID, user_id: UUID, action: str) -> None:
        """Обновляет подписки пользователя на канал."""
        exchange_name = settings.rabbitmq.exchange_name_template.format(company_id=company_id)
        routing_key = settings.rabbitmq.routing_key_template.format(channel_id=channel_id)

        exchange = await self._declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, auto_delete=True)

        queue = await self.declare_queue(user_id)

        logger.debug(
            f"Обновляю слушателя канала {channel_id} в компании {company_id} для пользователя {user_id} действие "
            f"{action}"
        )

        if action.lower() == "add":
            await queue.bind(exchange, routing_key)
        elif action.lower() == "remove":
            await queue.unbind(exchange, routing_key)
        else:
            logger.error(f"Неизвестный тип действия {action}")
            raise ValueError(f"Недопустимый тип действия {action}")

    async def declare_queue(self, user_id: UUID) -> AbstractQueue:
        """Создает или получает очередь."""
        queue_name = settings.rabbitmq.queue_name_template.format(user_id=user_id)
        return await self.channel.declare_queue(queue_name, exclusive=True)

    async def delete_queue(self, user_id: UUID) -> None:
        """Удаление очереди."""
        queue = await self.declare_queue(user_id)
        logger.debug(f"Отчищаю очередь для пользователя {user_id}")
        await queue.purge()
        logger.debug(f"Удаляю очередь пользователя {user_id}")
        await queue.delete()

    async def consume(self, user_id: UUID, callback: Callable[[str], Awaitable[None]]) -> None:
        """Получение сообщения из очереди."""
        queue = await self.declare_queue(user_id)
        async for message in queue:
            logger.debug("Получено сообщение из очереди")
            async with message.process():
                await callback(message.body.decode())

    async def close(self):
        """Закрытие подключения."""
        if self.connection:
            await self.connection.close()
