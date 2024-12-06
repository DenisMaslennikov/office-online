import os
import uuid

import aiofiles
from fastapi import UploadFile


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
