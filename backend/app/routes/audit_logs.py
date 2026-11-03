from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Dict, Any

from app.database.session import get_db
from app.auth.dependencies import require_admin
from app.models.user import User
from app.models.audit_log import AuditLog

router = APIRouter()

@router.get("/audit-logs")
def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    offset = (page - 1) * limit
    
    query = db.query(AuditLog).filter(AuditLog.business_id == current_user.business_id)
    total = query.count()
    
    logs = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
    
    data = []
    for log in logs:
        data.append({
            "id": log.id,
            "business_id": log.business_id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        })
        
    return {
        "items": data,
        "total": total,
        "page": page,
        "limit": limit
    }
