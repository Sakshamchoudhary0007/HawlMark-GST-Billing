from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.services import auth_service
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.utils.exceptions import AuthenticationError

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    user, _ = auth_service.register(db, data)
    token_data = {"sub": str(user.id), "business_id": str(user.business_id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data)
    )

@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, data.email, data.password)
    token_data = {"sub": str(user.id), "business_id": str(user.business_id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data)
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshRequest):
    token_data = decode_token(data.refresh_token)
    new_token_data = {"sub": str(token_data.user_id), "business_id": str(token_data.business_id), "role": token_data.role}
    return TokenResponse(
        access_token=create_access_token(new_token_data),
        refresh_token=create_refresh_token(new_token_data)
    )

@router.post("/logout")
def logout_user():
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
