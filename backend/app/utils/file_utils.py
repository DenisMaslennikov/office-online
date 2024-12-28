import os
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.config import settings
from app.constants import FileTypes


async def save_file(uploaded_file: UploadFile, destination: os.PathLike) -> str:
    """Сохраняет файл по указанному пути."""
    file_extension = os.path.splitext(uploaded_file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    if not os.path.exists(destination):
        os.makedirs(destination)
    file_path = os.path.join(destination, filename)
    async with aiofiles.open(file_path, "wb") as output_file:
        while content := await uploaded_file.read(1024):
            await output_file.write(content)
    return filename


async def delete_file(filename: str, destination: os.PathLike) -> None:
    """Удаляет файл по указанному пути."""
    file_path = os.path.join(destination, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


def validate_file_size(file: UploadFile, file_type: FileTypes) -> None:
    """Проверяет допустимый размер файла."""
    global USER_IMAGE
    match file_type:
        case USER_IMAGE:
            if file.size > settings.files.user_image_maximum_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Размер файла превышает максимально допустимый размер "
                    f"{settings.files.user_image_maximum_size / 1024 / 1024:.1f} Мегабайт",
                )


def validate_file_extension(file: UploadFile, file_type: FileTypes) -> None:
    """Проверяет допустимый типы файлов."""
    global USER_IMAGE
    match file_type:
        case USER_IMAGE:
            if os.path.splitext(file.filename)[1] not in settings.files.user_image_allowed_file_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Недопустимый тип файла разрешены только файлы "
                    f"{settings.files.user_image_allowed_file_types}",
                )
