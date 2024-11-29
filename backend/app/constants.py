import re
from pathlib import Path

from fastapi import status


# Регулярное выражение для проверки имени пользователя
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+$")

# ID организации "удаленная организация".
# TODO записать id специальной организации "удаленная организация"
# TODO дописать celery на удаление файлов связанных с удаленной организацией
DELETED_COMPANY_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"

# ID пользователя "Удаленный пользователь"
# TODO записать id специального пользователя "удаленный пользователь"
DELETED_USER_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"

# Корневая директория проекта.
BASE_DIR = Path(__file__).resolve().parent.parent

# Коды ответов по умолчанию.
DEFAULT_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    status.HTTP_404_NOT_FOUND: {"description": "User not found"},
}
