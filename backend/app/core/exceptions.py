"""Custom exceptions for the application."""

from typing import Any

from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base exception for application errors."""

    def __init__(
        self,
        code: int,
        message: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = None,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        self.detail = detail
        super().__init__(status_code=http_status, detail=message)


class UnauthorizedException(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            code=401,
            message=message,
            http_status=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenException(AppException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(
            code=403,
            message=message,
            http_status=status.HTTP_403_FORBIDDEN,
        )


class NotFoundException(AppException):
    """Raised when resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            code=404,
            message=message,
            http_status=status.HTTP_404_NOT_FOUND,
        )


class ValidationException(AppException):
    """Raised when input validation fails."""

    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(
            code=400,
            message=message,
            http_status=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictException(AppException):
    """Raised when resource conflicts with existing data."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(
            code=409,
            message=message,
            http_status=status.HTTP_409_CONFLICT,
        )


class InternalServerException(AppException):
    """Raised when an unexpected server error occurs."""

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(
            code=500,
            message=message,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
