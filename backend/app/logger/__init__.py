import logging
from logging.handlers import RotatingFileHandler

from app.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(settings.logs.app_log_level)

file_handler = RotatingFileHandler(
    settings.logs.app_log_file, maxBytes=settings.logs.app_max_bytes, backupCount=settings.logs.app_max_bytes
)

console_handler = logging.StreamHandler()

formatter = logging.Formatter(settings.logs.app_log_format)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
