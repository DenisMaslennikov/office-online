import uvicorn

from app import main_app
from app.config import settings
from app.uvicorn_log_settings import LOGGING_CONFIG

__all__ = ["main_app"]

if __name__ == "__main__":
    # Запуск сервера
    uvicorn.run("run:main_app", host="0.0.0.0", port=8000, reload=settings.reload, log_config=LOGGING_CONFIG)
