from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from app.core.config import SECRET_KEY, ALGORITHM, TOKEN_EXPIRE_HOURS

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:       return pwd.hash(p)
def verify_password(p: str, h: str) -> bool: return pwd.verify(p, h)

def create_token(data: dict, expire_minutes: Optional[int] = None) -> str:
    hours = TOKEN_EXPIRE_HOURS
    if expire_minutes is not None:
        delta = timedelta(minutes=expire_minutes)
    else:
        delta = timedelta(hours=hours)
    payload = {**data, "exp": datetime.now(timezone.utc) + delta}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
