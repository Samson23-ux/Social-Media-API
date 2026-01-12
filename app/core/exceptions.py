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

class UserNotFoundError(AppException):
    '''User not found'''

    pass

class UserExistsError(AppException):
    '''User already exists'''

    pass

class RoleExistsError(AppException):
    '''Role already exists'''

    pass

class ProfileImageError(AppException):
    '''Min and Max file not met'''

    pass

class ProfileImageExistsError(AppException):
    '''Profile images are complete'''

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




def create_exception_handler(
    initial_detail: dict, status_code: int
) -> callable[[Request, AppException], JSONResponse]:
    def exception_handler(req: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler
