from typing import Optional
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.auth.jwt import decode_token
from app.utils.exceptions import AuthenticationError, AuthorizationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    token_query: Optional[str] = Query(None, alias="token"),
    db: Session = Depends(get_db)
) -> User:
    raw_token = token_query or token
    if not raw_token:
        raise AuthenticationError("Not authenticated")
    token_data = decode_token(raw_token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise AuthenticationError("User not found")
    if user.business_id != token_data.business_id:
        raise AuthenticationError("Invalid token business context")
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != 'admin':
        raise AuthorizationError("Not enough permissions")
    return current_user
