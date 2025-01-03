from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants import BASE_DIR


class ApiV1Endpoints(BaseModel):
    """Эндпоинты первой версии апи."""

    users: str = "/users"
    websocket: str = "/ws"


class ApiV1(BaseModel):
    """Апи первой версии."""

    prefix: str = "/v1"
    endpoints: ApiV1Endpoints = ApiV1Endpoints()


class Api(BaseModel):
    """Апи."""

    prefix: str = "/api"
    v1: ApiV1 = ApiV1()


class DataBaseSettings(BaseModel):
    """Настройки подключения к базе данных."""

    postgres_db: str
    postgres_password: str
    postgres_user: str
    postgres_host: str
    postgres_port: str

    echo: bool = False

    @property
    def database_uri(self):
        """Свойство для получение db uri."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


class RedisSettings(BaseModel):
    """Настройки Redis."""

    host: str
    port: str

    default_ttl: int = None

    user_prefix: str = "user"
    username_prefix: str = "username"
    timezone_prefix: str = "timezone"

    ttl_override: dict[str, int | None] = {
        user_prefix: None,
        timezone_prefix: None,
    }


class RabbitMQSettings(BaseModel):
    """Настройки RabbitMQ."""

    host: str
    port: int
    user: str
    password: str

    exchange_name_template: str = "company_{company_id}"
    routing_key_template: str = "{type}_chanel_{channel_id}"
    queue_name_template: str = "user_{user_id}"


class LoggerSettings(BaseModel):
    """Настройка логирования."""

    logs_dir: Path = BASE_DIR.parent / "logs"
    app_log_file: Path = logs_dir / "app.log"
    uvicorn_log_file: Path = logs_dir / "uvicorn.log"
    uvicorn_log_level: str = "INFO"
    uvicorn_custom_log_format: str = (
        "%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
    )
    uvicorn_standard_log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    uvicorn_max_bytes: int = 1024 * 1024 * 10  # 10 Мегабайт
    uvicorn_backup_count: int = 5
    app_log_format: str = "%(asctime)s | %(levelname)s | %(funcName)s | %(lineno)d | %(message)s"
    app_log_level: str = "DEBUG"
    app_max_bytes: int = 1024 * 1024 * 10  # 10 Мегабайт
    app_backup_count: int = 5


class JWTSettings(BaseModel):
    """Конфигурация настроек безопасности."""

    # Пути к приват и паблик ключам
    private_key_path: Path = BASE_DIR / "certs" / "private_key"
    public_key_path: Path = BASE_DIR / "certs" / "public_key.pub"
    algorithm: str = "RS256"
    access_token_expires_delta: timedelta = timedelta(days=365)
    refresh_token_expires_delta: timedelta = timedelta(days=7)


class FilesSettings(BaseModel):
    """Настройки хранения файлов."""

    uploads_path: Path = BASE_DIR.parent / "uploads"
    users_images_path: Path = uploads_path / "users" / "images"
    user_image_maximum_size: int = 1024 * 1024 * 8  # 8MB
    user_image_allowed_file_types: list[str] = [".png", ".jpg", ".jpeg", ".gif"]


class FilesUrlsSettings(BaseModel):
    """Пути к файлам для формирования url."""

    media: str
    users_images_url: str


class UsersSettings(BaseModel):
    """Настройки пользователей."""

    # Интервал времени для удаления пользователя
    # TODO Написать задачу для Celery для удаления пользователя
    user_deletion_timedelta: timedelta = timedelta(days=30)


class CompaniesSettings(BaseModel):
    """Настройки компании."""

    # Интервал времени для удаления компании
    # TODO Написать задачу для Celery для удаления компании
    company_deletion_timedelta: timedelta = timedelta(days=30)


class WebSocketsSettings(BaseModel):
    """Настройки подключения по websocket."""

    # Максимальный размер сообщения которое может обработать websocket.
    max_websocket_message_size: int = 1024 * 4  # 4 KB

    # Интервал heartbeat в миллисекундах.
    heartbeat_interval: int = 1000 * 60 * 60 * 24  # 1 день

    # Интервал в секундах по истечению которого связь считается разорванной.
    timeout_interval: int = heartbeat_interval / 1000 * 3


class Settings(BaseSettings):
    """Конфигурация бекенда."""

    # Настройки пользователей
    users: UsersSettings = UsersSettings()
    # Настройка компаний
    companies: CompaniesSettings = CompaniesSettings()

    # Настройки websocket.
    websocket: WebSocketsSettings = WebSocketsSettings()

    # Настройки подключения к базе данных
    db: DataBaseSettings

    # Настройки Redis.
    redis: RedisSettings

    # Настройки RabbitMQ
    rabbitmq: RabbitMQSettings

    # Настройки логирования
    logs: LoggerSettings = LoggerSettings()

    # Надо ли отслеживать изменения в файлах и перезапускать uvicorn
    reload: bool = True
    debug: bool

    # Хранение файлов.
    files: FilesSettings = FilesSettings()

    # Раздача файлов через Nginx
    files_urls: FilesUrlsSettings

    # Структура эндпоинтов API
    api: Api = Api()

    # Настройки безопасности
    jwt: JWTSettings = JWTSettings()

    model_config = SettingsConfigDict(case_sensitive=False, env_prefix="API_", env_nested_delimiter="__")


settings = Settings()
