from __future__ import annotations
from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('business_id', 'email', name='uix_business_email'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('businesses.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default='admin')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Relationships
    business: Mapped["Business"] = relationship('Business', back_populates='users')
