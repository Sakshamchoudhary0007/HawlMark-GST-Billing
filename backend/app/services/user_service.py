from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.password import hash_password
from app.utils.exceptions import ConflictError, NotFoundError
from app.services.audit_service import log_action

def list_users(db: Session, business_id: int) -> list[User]:
    return db.query(User).filter(User.business_id == business_id).all()

def create_user(db: Session, business_id: int, data: UserCreate, acting_user_id: int) -> User:
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise ConflictError("Email already registered")

    user = User(
        business_id=business_id,
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_action(
        db=db,
        business_id=business_id,
        user_id=acting_user_id,
        action="CREATE_USER",
        entity_type="USER",
        entity_id=user.id,
        metadata={"role": user.role, "email": user.email}
    )

    return user

def update_user_role(db: Session, business_id: int, target_user_id: int, role: str, acting_user_id: int) -> User:
    user = db.query(User).filter(User.id == target_user_id, User.business_id == business_id).first()
    if not user:
        raise NotFoundError("User not found")

    old_role = user.role
    user.role = role
    db.commit()
    db.refresh(user)

    log_action(
        db=db,
        business_id=business_id,
        user_id=acting_user_id,
        action="UPDATE_USER_ROLE",
        entity_type="USER",
        entity_id=user.id,
        metadata={"old_role": old_role, "new_role": role}
    )

    return user

def toggle_user_status(db: Session, business_id: int, target_user_id: int, is_active: bool, acting_user_id: int) -> User:
    user = db.query(User).filter(User.id == target_user_id, User.business_id == business_id).first()
    if not user:
        raise NotFoundError("User not found")

    user.is_active = is_active
    db.commit()
    db.refresh(user)

    log_action(
        db=db,
        business_id=business_id,
        user_id=acting_user_id,
        action="TOGGLE_USER_STATUS",
        entity_type="USER",
        entity_id=user.id,
        metadata={"is_active": is_active}
    )

    return user
