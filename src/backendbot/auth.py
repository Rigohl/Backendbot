"""Authentication utilities for API endpoints."""

from fastapi import Depends, HTTPException, status

from .config import settings


def get_api_key(
    api_key: str = Depends(
        HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    )
) -> str:
    """Validate the API Key provided in the request header.

    Args:
        api_key (str): The API key from the request header.

    Returns:
        str: The API key if valid.

    Raises:
        HTTPException: If the API key is invalid.

    """
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
    )
