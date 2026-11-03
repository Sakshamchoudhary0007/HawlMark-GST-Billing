from sqlalchemy import Column, BigInteger, String, Boolean, DECIMAL, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = 'products'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_id = Column(BigInteger, ForeignKey('businesses.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True)
    hsn_sac = Column(String(20), nullable=True)
    unit = Column(String(30), nullable=True)
    default_rate = Column(DECIMAL(19, 4), nullable=False, default=0.0000)
    gst_rate = Column(DECIMAL(5, 2), nullable=False, default=0.00)
    category = Column(String(100), nullable=True)
    is_archived = Column(Boolean, nullable=False, default=False)
    
    business = relationship('Business')
    
    __table_args__ = (
        Index('ix_products_business_name', 'business_id', 'name'),
        Index('ix_products_business_sku', 'business_id', 'sku'),
        Index('ix_products_business_hsn', 'business_id', 'hsn_sac'),
        {'mysql_charset': 'utf8mb4'}
    )
