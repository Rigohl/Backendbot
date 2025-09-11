from fastapi import Depends, HTTPException, status

from .config import settings

def get_api_key(
    api_key: str = Depends(lambda: None)
) -> str:
    """Dependency to validate the API Key provided in the request header.

    Args:
        api_key (str): The API key from the request header.

    Returns:
        str: The API key if valid.

    Raises:
        HTTPException: If the API key is invalid.

    """
    from fastapi import Header
    # Get API key from header
    if api_key is None:
        import inspect
        frame = inspect.currentframe().f_back
        request = frame.f_locals.get('request', None)
        if request:
            api_key = request.headers.get('X-API-Key')
    if api_key == settings.API_KEY:
        return api_key
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
