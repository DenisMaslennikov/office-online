from app.config import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {"format": settings.logs.uvicorn_standard_log_format},
        "custom_formatter": {"format": settings.logs.uvicorn_custom_log_format},
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "stream_handler": {
            "formatter": "custom_formatter",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "formatter": "custom_formatter",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.logs.uvicorn_log_file,
            "maxBytes": settings.logs.uvicorn_max_bytes,
            "backupCount": settings.logs.uvicorn_backup_count,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["default", "file_handler"],
            "level": settings.logs.uvicorn_log_level,
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default", "file_handler"],
            "level": settings.logs.uvicorn_log_level,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default", "file_handler"],
            "level": settings.logs.uvicorn_log_level,
            "propagate": False,
        },
        "uvicorn.asgi": {
            "handlers": ["stream_handler", "file_handler"],
            "level": settings.logs.uvicorn_log_level,
            "propagate": False,
        },
    },
}
