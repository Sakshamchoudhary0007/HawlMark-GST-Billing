from __future__ import annotations
from typing import Optional
from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

DEFAULT_INVOICE_TERMS = """1. E. & O.E.
2. Received the precious metal / Jewellery in satisfactory Condition.
3. Subject to 'Palghar' Jurisdiction only."""

class Business(Base, TimestampMixin):
    __tablename__ = 'businesses'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    licence_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Bank details
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_ifsc: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # Invoice settings
    invoice_prefix: Mapped[Optional[str]] = mapped_column(String(30), nullable=True, default='INV')
    invoice_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=DEFAULT_INVOICE_TERMS)
    invoice_footer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signatory_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    users: Mapped[list["User"]] = relationship('User', back_populates='business', lazy='select')
