from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from app.main import app
from app.core.exceptions import (
    create_exception_handler,
    ServerError,
    AuthenticationError,
    AuthorizationError,
    UserNotFoundError,
)

error_time: datetime = datetime.now(timezone.utc)


@app.exception_handler(500)
def server_error_handler(req, exc):
    return JSONResponse(
        content={'error_code': 'Internal Server error', 'timestamp': error_time},
        status_code=500,
    )


app.add_exception_handler(
    exc_class_or_status_code=ServerError,
    handler=create_exception_handler(
        status_code=500,
        initial_detail={
            'error_code': 'Server error',
            'message': 'Oops! Something went wrong',
            'timestamp': error_time,
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=AuthenticationError,
    handler=create_exception_handler(
        status_code=401,
        initial_detail={
            'error_code': 'User Not Authenticated',
            'message': 'User should sign up or sign in to accesss resource',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=AuthorizationError,
    handler=create_exception_handler(
        status_code=403,
        initial_detail={
            'error_code': 'User Not Authorized',
            'message': 'User does not have access to make the requested change',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=UserNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'User not found',
            'message': 'User not found with the provided user info',
            'resolution': 'Confirm that the sent details matches the user details',
            'timestamp': error_time,
        },
    ),
)

