from fastapi.requests import Request
from fastapi.responses import JSONResponse


# Base Exception which other exceptions inherit from
class AppException(Exception):
    '''Base Exception for app'''

    pass


def create_exception_handler(
    initial_detail: dict, status_code: int
) -> callable[[Request, AppException], JSONResponse]:
    def exception_handler(req: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler
