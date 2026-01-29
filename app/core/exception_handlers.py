from datetime import datetime, timezone
from fastapi.responses import JSONResponse

from app.main import app
from app.core.exceptions import (
    create_exception_handler,
    ServerError,
    UsernameError,
    PasswordError,
    CredentialError,
    RoleExistsError,
    UserExistsError,
    ImageUploadError,
    UserNotFoundError,
    PostNotFoundError,
    InvalidImageError,
    UsersNotFoundError,
    AuthorizationError,
    PostsNotFoundError,
    PostVisibilityError,
    AuthenticationError,
    AvatarNotFoundError,
    CommentNotFoundError,
    CommentsNotFoundError,
    FollowingNotFoundError,
    FollowersNotFoundError,
    PostImageNotFoundError,
    ProfileImageExistsError,
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
    exc_class_or_status_code=UsersNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Users not found',
            'message': 'No users at the moment. Check back later!',
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
    exc_class_or_status_code=ImageUploadError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Image upload error',
            'message': f'A minimum of {min_profile_image} and maximum of {max_profile_image} are allowed',
            'timestamp': error_time,
        },
    ),
)


app.add_exception_handler(
    exc_class_or_status_code=AvatarNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Avatar not found',
            'message': 'No Avatar found for the provided user',
            'resolution': 'Ensure the provided image url is correct',
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

app.add_exception_handler(
    exc_class_or_status_code=FollowersNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Followers not found',
            'message': 'User does not have any followers',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=FollowingNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Following not found',
            'message': 'User has not followed any account',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=CommentsNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Comments not found',
            'message': 'No comments found at the moment',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=CommentNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Comment not found',
            'message': 'No comment found with the provided id',
            'resolution': 'Confirm that the sent id matches the comment id',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PostsNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Posts not found',
            'message': 'No Posts found at the moment',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PostNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Post not found',
            'message': 'No Post found with the provided id',
            'resolution': 'Confirm that the sent id matches the post id',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PostVisibilityError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Invalid post visibility provided',
            'message': 'Post visibility can either be public, followers or private',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=PostImageNotFoundError,
    handler=create_exception_handler(
        status_code=404,
        initial_detail={
            'error_code': 'Post image not found',
            'message': 'No post image found for the provided url',
            'resolution': 'Ensure the provided image url is correct',
            'timestamp': error_time,
        },
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidImageError,
    handler=create_exception_handler(
        status_code=400,
        initial_detail={
            'error_code': 'Invalid image uploaded',
            'message': 'User uploaded an invalid image format',
            'resolution': 'Check that the file type uploaded is an image',
            'timestamp': error_time,
        },
    ),
)
