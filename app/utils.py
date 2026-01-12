import aiofiles
from fastapi import UploadFile

from app.core.exceptions import ServerError

async def write_file(filepath: str, file: UploadFile):
    try:
        async with aiofiles.open(filepath, 'wb+') as f:
            await f.write(await file.read())
    except Exception as e:
        raise ServerError() from e
