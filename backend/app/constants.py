import enum
import re
from datetime import timedelta
from pathlib import Path
from typing import AnyStr

from fastapi import status

# Регулярное выражение для проверки имени пользователя
USERNAME_REGEX: re.Pattern[AnyStr] = re.compile(r"^[a-zA-Z0-9_.+-]+$")

# ID организации "удаленная организация".
# TODO записать id специальной организации "удаленная организация"
# TODO дописать celery на удаление файлов связанных с удаленной организацией
DELETED_COMPANY_ID: str = "dddddddd-dddd-dddd-dddd-dddddddddddd"

# ID пользователя "Удаленный пользователь"
# TODO записать id специального пользователя "удаленный пользователь"
DELETED_USER_ID: str = "dddddddd-dddd-dddd-dddd-dddddddddddd"

# ID Иконки для файлов по умолчанию.
# TODO Заменить на id иконки для группы файлов по умолчанию
DEFAULT_FILE_GROUP_ICON_ID: int = 1

# ID Иконки для проекта по умолчанию.
# TODO Заменить на id иконки для проекта по умолчанию
DEFAULT_PROJECT_ICON_ID: int = 2

# ID Иконки для типа задачи по умолчанию.
# TODO Заменить на id иконки для типа задачи по умолчанию
DEFAULT_TASK_TYPE_ICON_ID: int = 3

# ID удаленного сообщения.
# TODO Заменить на id удаленного сообщения
DELETED_MESSAGE_ID: int = 1

# Интервал по умолчанию для удаления компании.
# TODO Написать задачу для Celery для удаления компании
COMPANY_DELETION_TIMEDELTA: timedelta = timedelta(days=30)

# Корневая директория проекта.
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Коды ответов по умолчанию.
DEFAULT_RESPONSES: dict[int, dict[str, str]] = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Ошибка авторизации"},
    status.HTTP_403_FORBIDDEN: {"description": "Пользователь не активен или недостаточно прав"},
    status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
}


# Типы файлов
@enum.unique
class FileTypes(enum.Enum):
    """Enum хранилище типов файлов."""

    USER_IMAGE: str = "USER_IMAGE"


@enum.unique
class RabbitMQRoutingKeysTypes(enum.Enum):
    """Типы ключей маршрутизации для RabbitMQ."""

    TYPING: str = "TYPING"
    MESSAGES: str = "MESSAGES"
    MESSAGES_BODY: str = "MESSAGES_BODY"
