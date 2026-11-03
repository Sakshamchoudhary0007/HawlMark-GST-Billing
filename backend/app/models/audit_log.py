from __future__ import annotations
import json
from datetime import datetime
from sqlalchemy import BigInteger, Column, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_id = Column(BigInteger, ForeignKey("businesses.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    business = relationship("Business")
    user = relationship("User")

    __table_args__ = (
        Index("ix_audit_bus_date", "business_id", "created_at"),
        {"mysql_charset": "utf8mb4"},
    )
