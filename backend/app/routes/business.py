from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.business import BusinessUpdate, BusinessResponse
from app.services import business_service
from app.auth.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter()

@router.get("/business", response_model=BusinessResponse)
def get_business(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business = business_service.get_business(db, current_user.business_id)
    return business

@router.put("/business", response_model=BusinessResponse)
def update_business(
    data: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    business = business_service.update_business(db, current_user.business_id, data)
    return business
