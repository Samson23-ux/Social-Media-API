import aiofiles
import sentry_sdk
from PIL import Image
from fastapi import UploadFile
from sentry_sdk import logger as sentry_logger

from app.core.exceptions import ServerError


async def write_file(filepath: str, file: UploadFile):
    try:
        async with aiofiles.open(filepath, 'wb+') as f:
            await f.write(await file.read())
            sentry_logger.info('Image {name} saved to disk', name=file.filename)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        sentry_logger.error(
            'Internal server error while saving image {name} to disk',
            name=file.filename,
        )
        raise ServerError() from e


async def validate_image(file: UploadFile):
    try:
        await file.seek(0)
        with Image.open(file.file) as f:
            f.verify()
        await file.seek(0)
        return True
    except (IOError, SyntaxError) as e:
        sentry_sdk.capture_exception(e)
        sentry_logger.error('Error occured while validating image upload')
        return False
