from __future__ import annotations

from sqlalchemy import Column, BigInteger, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base

class InvoiceSequence(Base):
    __tablename__ = 'invoice_sequences'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_id = Column(BigInteger, ForeignKey('businesses.id'), nullable=False, index=True)
    financial_year = Column(String(20), nullable=False)
    prefix = Column(String(30), nullable=False, default='INV')
    next_number = Column(BigInteger, nullable=False, default=1)
    
    __table_args__ = (
        UniqueConstraint('business_id', 'financial_year', 'prefix', name='uix_bus_fy_prefix'),
        {'mysql_charset': 'utf8mb4'}
    )
    
    business = relationship('Business')
