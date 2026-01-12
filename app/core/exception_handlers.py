from fastapi.responses import JSONResponse
from datetime import datetime, timezone

from app.main import app
from app.core.exceptions import (
    create_exception_handler,
    ServerError,
    AuthenticationError,
    AuthorizationError,
    UserNotFoundError,
    UserExistsError,
    RoleExistsError,
    ProfileImageExistsError,
    ProfileImageError,
    CredentialError,
    PasswordError,
    UsernameError,
)

error_time: datetime = datetime.now(timezone.utc).isoformat()
min_profile_image = 1
max_profile_image = 2


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

app.add_exception_handler(
    exc_class_or_status_code=UserExistsError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'User already exists',
            'message': 'User already exists with the provided username or email',
            'resolution': 'Check the provided username or email to confirm if does not exist already',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=RoleExistsError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Role already exists',
            'message': 'An identical Role exist already',
            'resolution': 'Check the provided role to confirm if does not exist already',
            'timestamp': error_time,
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=ProfileImageExistsError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Profile images are complete',
            'message': 'User already uploaded avatar and header images',
            'resolution': 'Delete the current profile images to upload a new one',
            'timestamp': error_time,
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=ProfileImageError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Profile images are complete',
            'message': f'A minimum of {min_profile_image} and maximum of {max_profile_image} are allowed',
            'timestamp': error_time,
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=CredentialError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Invalid credentials',
            'message': 'User provided Invalid credentials for sign in',
            'resolution': 'Re-check the provided credentials for confirmation',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PasswordError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Incorrect password',
            'message': 'User password is incorrect ',
            'resolution': 'Re-check the provided password to confirm its validity',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=UsernameError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Invalid username',
            'message': 'Username is not valid ',
            'resolution': 'Username must have a minimum length of 6 characters and can only contain underscores(_) e.g -> @user_example',
            'timestamp': error_time,
        },
    ),
)
