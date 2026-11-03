from sqlalchemy.orm import Session
from app.models.user import User
from app.models.business import Business
from app.schemas.auth import RegisterRequest
from app.auth.password import hash_password, verify_password
from app.utils.exceptions import AuthenticationError, ConflictError

def register(db: Session, data: RegisterRequest) -> tuple[User, Business]:
    # Check if email already exists globally
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise ConflictError("Email already registered")
        
    business = Business(legal_name=data.business_name)
    db.add(business)
    db.flush()
    
    user = User(
        business_id=business.id,
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role='admin',
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(business)
    db.refresh(user)
    return user, business

def authenticate(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise AuthenticationError("Invalid email or password")
    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    return user
