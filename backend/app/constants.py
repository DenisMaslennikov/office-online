import re
from pathlib import Path

from fastapi import status


# Регулярное выражение для проверки имени пользователя
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+$")

# Корневая директория проекта.
BASE_DIR = Path(__file__).resolve().parent.parent

# Коды ответов по умолчанию.
DEFAULT_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    status.HTTP_403_FORBIDDEN: {"description": "Forbidden"},
    status.HTTP_404_NOT_FOUND: {"description": "User not found"},
}
