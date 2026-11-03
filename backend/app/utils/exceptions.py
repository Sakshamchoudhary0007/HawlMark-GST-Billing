from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details or {}


class NotFoundError(AppException):
    """Resource not found (404)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(404, "NOT_FOUND", message, details)


class ValidationError(AppException):
    """Validation failed (422)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(422, "VALIDATION_ERROR", message, details)


class AuthenticationError(AppException):
    """Authentication failed (401)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(401, "AUTHENTICATION_ERROR", message, details)


class AuthorizationError(AppException):
    """Authorization failed (403)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(403, "AUTHORIZATION_ERROR", message, details)


class ConflictError(AppException):
    """Resource conflict (409)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(409, "CONFLICT", message, details)


class BusinessLogicError(AppException):
    """Business logic violation (400)."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(400, "BUSINESS_LOGIC_ERROR", message, details)


# Alias for backward compatibility / convenience
BadRequestError = BusinessLogicError
