from fastapi import HTTPException, status

class ServiceException(HTTPException):
    """Base exception for service-level errors with a custom error code.

    Attributes:
        status_code (int): HTTP status code.
        detail (str): A human-readable explanation of the error.
        code (str): A unique, machine-readable error code.
    """
    def __init__(self, status_code: int, detail: str, code: str = "SERVICE_ERROR"):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class ResourceNotFoundException(ServiceException):
    """Exception raised when a requested resource is not found (404)."""
    def __init__(self, detail: str = "Resource not found", code: str = "NOT_FOUND"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, code=code)

class UnauthorizedException(ServiceException):
    """Exception raised for authentication failures (401)."""
    def __init__(self, detail: str = "Authentication required", code: str = "UNAUTHORIZED"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, code=code)

class ForbiddenException(ServiceException):
    """Exception raised for authorization failures (403)."""
    def __init__(self, detail: str = "Permission denied", code: str = "FORBIDDEN"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, code=code)

class BadRequestException(ServiceException):
    """Exception raised for bad requests (400)."""
    def __init__(self, detail: str = "Bad request", code: str = "BAD_REQUEST"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, code=code)

class InternalServerErrorException(ServiceException):
    """Exception raised for internal server errors (500)."""
    def __init__(self, detail: str = "Internal server error", code: str = "INTERNAL_SERVER_ERROR"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail, code=code)
