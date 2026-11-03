from __future__ import annotations
import json
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    business_id: int,
    user_id: Optional[int],
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> AuditLog:
    actual_user_id = user_id if (user_id and user_id > 0) else None

    logger.info(
        f"Audit Log: business_id={business_id} user_id={actual_user_id} action={action} "
        f"entity_type={entity_type} entity_id={entity_id} metadata={metadata}"
    )

    details_str = json.dumps(metadata) if metadata else None

    audit_log = AuditLog(
        business_id=business_id,
        user_id=actual_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details_str
    )
    db.add(audit_log)
    db.flush()
    return audit_log
