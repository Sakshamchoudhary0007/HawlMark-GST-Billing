from __future__ import annotations

from sqlalchemy import Column, BigInteger, String, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_id = Column(BigInteger, ForeignKey("businesses.id"), nullable=False, index=True)
    customer_name = Column(String(255), nullable=False)
    gstin = Column(String(15), nullable=True)
    licence_number = Column(String(100), nullable=True)
    pan_number = Column(String(10), nullable=True)
    mobile = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    state_code = Column(String(5), nullable=True)
    pincode = Column(String(10), nullable=True)
    place_of_supply = Column(String(150), nullable=True)
    taxpayer_type = Column(String(50), nullable=True)
    gst_verification_status = Column(String(40), nullable=True)
    gst_verified_at = Column(DateTime, nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)

    # Relationships
    business = relationship("Business")

    __table_args__ = (
        Index("ix_customers_business_name", "business_id", "customer_name"),
        Index("ix_customers_business_gstin", "business_id", "gstin"),
        Index("ix_customers_business_licence", "business_id", "licence_number"),
        Index("ix_customers_business_mobile", "business_id", "mobile"),
        {"mysql_charset": "utf8mb4"},
    )
