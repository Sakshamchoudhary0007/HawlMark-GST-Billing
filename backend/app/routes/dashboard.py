from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services import dashboard_service

router = APIRouter()

@router.get("/dashboard/summary", response_model=Dict[str, Any])
def get_dashboard_summary_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary statistics and recent data for the business.
    """
    return dashboard_service.get_dashboard_summary(db, current_user.business_id)
