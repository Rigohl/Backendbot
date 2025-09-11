from fastapi import Depends, HTTPException, status, Header

from .config import settings

def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key")
) -> str:
    """Dependency to validate the API Key provided in the request header.

    Args:
        x_api_key (str): The API key from the request header (X-API-Key).

    Returns:
        str: The API key if valid.

    Raises:
        HTTPException: If the API key is invalid.

    """
    if x_api_key == settings.API_KEY:
        return x_api_key
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
