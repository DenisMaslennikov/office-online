import logging
from logging.handlers import RotatingFileHandler

from app.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(settings.logs.log_level)

file_handler = RotatingFileHandler(
    settings.logs.log_file, maxBytes=settings.logs.max_bytes, backupCount=settings.logs.backup_count
)

console_handler = logging.StreamHandler()

file_handler.setFormatter(settings.logs.app_log_format)
console_handler.setFormatter(settings.logs.app_log_format)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
