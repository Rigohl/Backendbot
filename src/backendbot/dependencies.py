from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class TokenData(BaseModel):
    username: str | None = None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

async def get_current_active_user(current_user: TokenData = Depends(get_current_user)):
    # Here you can add more checks, e.g., if the user is active in a database
    return current_user

# Keeping get_api_key for now, but it will be replaced by get_current_active_user
# in api_routes.py. This is a temporary step.
def get_api_key(
    x_api_key: str = Header(None, alias="X-API-Key") # Changed default to None
) -> str:
    """Dependency to validate the API Key provided in the request header.
    This function will be deprecated in favor of JWT authentication.
    """
    if x_api_key == settings.API_KEY:
        return x_api_key
    # If API key is not provided or invalid, it will be handled by JWT later
    return "" # Return empty string if not matched, will be handled by other auth
