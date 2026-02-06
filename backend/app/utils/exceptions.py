"""Custom exceptions for the application."""

from typing import Optional


class ConceptPilotException(Exception):
    """Base exception for ConceptPilot application."""

    def __init__(self, message: str, status_code: int = 400):
        """Initialize exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(ConceptPilotException):
    """Raised when data validation fails."""

    def __init__(self, message: str):
        super().__init__(message, 422)


class NotFoundError(ConceptPilotException):
    """Raised when a resource is not found."""

    def __init__(self, resource: str, resource_id: str = ""):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, 404)


class UnauthorizedError(ConceptPilotException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(ConceptPilotException):
    """Raised when user lacks permission."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class ConflictError(ConceptPilotException):
    """Raised when there's a resource conflict."""

    def __init__(self, message: str):
        super().__init__(message, 409)


class DuplicateError(ConflictError):
    """Raised when trying to create a duplicate resource."""

    def __init__(self, resource: str):
        message = f"{resource} already exists"
        super().__init__(message)


class DatabaseError(ConceptPilotException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database error"):
        super().__init__(message, 500)


class LessonGenerationError(ConceptPilotException):
    """Raised when lesson generation fails."""

    def __init__(self, message: str = "Failed to generate lesson"):
        super().__init__(message, 500)


class ConfigurationError(ConceptPilotException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(message, 500)
