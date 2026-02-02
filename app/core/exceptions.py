# defer type hint evaluation
# this converts type hints to string at import time
from __future__ import annotations

from fastapi.requests import Request
from fastapi.responses import JSONResponse


# Base Exception which other exceptions inherit from
class AppException(Exception):
    '''Base Exception for app'''

    pass

class ServerError(AppException):
    '''Internal Server Error'''

    pass

class AuthenticationError(AppException):
    '''User Not Authenticated'''

    pass

class AuthorizationError(AppException):
    '''User Not Authorized'''

    pass

class UsersNotFoundError(AppException):
    '''Users not found'''

    pass

class UserNotFoundError(AppException):
    '''User not found'''

    pass

class UserExistsError(AppException):
    '''User already exists'''

    pass

class FollowersNotFoundError(AppException):
    '''Followers not found'''

    pass

class FollowingNotFoundError(AppException):
    '''Following not found'''

    pass


class RoleExistsError(AppException):
    '''Role already exists'''

    pass

class AvatarUploadError(AppException):
    '''Min and Max image not met'''

    pass

class PostUploadError(AppException):
    '''Min image not met'''

    pass

class ProfileImageExistsError(AppException):
    '''Profile images are complete'''

    pass

class AvatarNotFoundError(AppException):
    '''user avatar not found'''

    pass

class CredentialError(AppException):
    '''User provided invalid credentials'''

    pass

class PasswordError(AppException):
    '''User provided incorrect password'''

    pass

class UsernameError(AppException):
    '''Invalid username'''

    pass

class CommentsNotFoundError(AppException):
    '''comments not found'''

    pass

class CommentNotFoundError(AppException):
    '''comment not found'''

    pass

class PostsNotFoundError(AppException):
    '''posts not found'''

    pass

class PostNotFoundError(AppException):
    '''post not found'''

    pass

class PostVisibilityError(AppException):
    '''incorrect visibility provided'''

    pass

class PostImageNotFoundError(AppException):
    '''post image not found'''

    pass

class InvalidImageError(AppException):
    '''inavlid image uploaded'''

    pass


class UserFollowError(AppException):
    '''attempt to follow same account'''

    pass

class UserUnfollowError(AppException):
    '''attempt to unfollow same account'''

    pass


def create_exception_handler(
    initial_detail: dict, status_code: int
) -> callable[[Request, AppException], JSONResponse]:
    def exception_handler(req: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler
