import os
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import decode_token
from app.core.config import OPENAI_API_KEY

_bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    try:
        return decode_token(creds.credentials)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

def get_api_key(x_api_key: str = Header(default="")) -> str:
    key = x_api_key or OPENAI_API_KEY
    if not key:
        raise HTTPException(status_code=401, detail="OpenAI API key required")
    return key
