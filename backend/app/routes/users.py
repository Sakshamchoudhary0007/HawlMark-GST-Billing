from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.auth.dependencies import require_admin
from app.models.user import User
from app.schemas.user import UserCreate, UserRoleUpdate, UserStatusUpdate, UserResponse, UserListResponse
from app.services import user_service

router = APIRouter()

@router.get("", response_model=UserListResponse)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = user_service.list_users(db=db, business_id=current_user.business_id)
    return UserListResponse(items=users, total=len(users))

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = user_service.create_user(
        db=db,
        business_id=current_user.business_id,
        data=data,
        acting_user_id=current_user.id
    )
    return user

@router.patch("/{id}/role", response_model=UserResponse)
def update_user_role(
    id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = user_service.update_user_role(
        db=db,
        business_id=current_user.business_id,
        target_user_id=id,
        role=data.role,
        acting_user_id=current_user.id
    )
    return user

@router.patch("/{id}/status", response_model=UserResponse)
def toggle_user_status(
    id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = user_service.toggle_user_status(
        db=db,
        business_id=current_user.business_id,
        target_user_id=id,
        is_active=data.is_active,
        acting_user_id=current_user.id
    )
    return user
