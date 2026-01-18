import aiofiles
import sentry_sdk
from fastapi import UploadFile
from sentry_sdk import logger as sentry_logger

from app.core.exceptions import ServerError

async def write_file(filepath: str, file: UploadFile):
    try:
        async with aiofiles.open(filepath, 'wb+') as f:
            await f.write(await file.read())
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_logger.error('Error writing image {name} to disk', name=file.filename)
        raise ServerError() from e
