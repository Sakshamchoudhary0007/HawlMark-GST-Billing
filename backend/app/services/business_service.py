from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from app.models.business import Business
from app.schemas.business import BusinessUpdate
from app.utils.exceptions import NotFoundError
from app.services import audit_service

def get_business(db: Session, business_id: int) -> Business:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise NotFoundError("Business not found")
    return business

def update_business(db: Session, business_id: int, data: BusinessUpdate) -> Business:
    business = get_business(db, business_id)
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(business, key, value)
        
    db.commit()
    db.refresh(business)
    
    # Passing user_id=0 as it is not passed to the service. Realistically, we should pass user_id or handle it in route.
    audit_service.log_action(
        db=db,
        business_id=business_id,
        user_id=0,
        action="UPDATE",
        entity_type="BUSINESS",
        entity_id=business_id,
        metadata=update_data
    )
    
    return business
