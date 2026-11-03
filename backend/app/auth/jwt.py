from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel
from app.config.settings import get_settings
from app.utils.exceptions import AuthenticationError

settings = get_settings()

class TokenData(BaseModel):
    user_id: int
    business_id: int
    role: str

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        business_id = payload.get("business_id")
        role = payload.get("role")
        if user_id is None or business_id is None or role is None:
            raise AuthenticationError("Could not validate credentials")
        return TokenData(user_id=int(user_id), business_id=int(business_id), role=role)
    except JWTError:
        raise AuthenticationError("Could not validate credentials or token expired")
