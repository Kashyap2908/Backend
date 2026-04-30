from rest_framework import status


class BaseAppException(Exception):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "INTERNAL_ERROR"

    def __init__(self, message="An unexpected error occurred", details=None):
        super().__init__(message)
        self.message = message
        self.details = details


class AuthenticationError(BaseAppException):
    http_status = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"

    def __init__(self, message="Authentication required", details=None):
        super().__init__(message, details)


class AuthorizationError(BaseAppException):
    http_status = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_ERROR"

    def __init__(self, message="You do not have permission to perform this action", details=None):
        super().__init__(message, details)


class ValidationError(BaseAppException):
    http_status = status.HTTP_400_BAD_REQUEST
    error_code = "VALIDATION_ERROR"

    def __init__(self, message="Invalid input data", details=None):
        super().__init__(message, details)


class NotFoundError(BaseAppException):
    http_status = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"

    def __init__(self, message="Resource not found", details=None):
        super().__init__(message, details)


class DatabaseError(BaseAppException):
    http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "DATABASE_ERROR"

    def __init__(self, message="A database error occurred", details=None):
        super().__init__(message, details)


class ConflictError(BaseAppException):
    http_status = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"

    def __init__(self, message="Resource already exists", details=None):
        super().__init__(message, details)
