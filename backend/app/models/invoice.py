from __future__ import annotations

from sqlalchemy import Column, BigInteger, String, Date, Boolean, Numeric, Text, DateTime, ForeignKey, UniqueConstraint, Integer
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin

class Invoice(Base, TimestampMixin):
    __tablename__ = 'invoices'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_id = Column(BigInteger, ForeignKey('businesses.id'), nullable=False, index=True)
    customer_id = Column(BigInteger, ForeignKey('customers.id'), nullable=True, index=True)
    invoice_number = Column(String(100), nullable=True)
    invoice_date = Column(Date, nullable=False)
    tax_mode = Column(String(20), nullable=False, default='CGST_SGST')
    reverse_charge = Column(Boolean, nullable=False, default=False)
    subtotal = Column(Numeric(19, 4), nullable=False, default=0.0000)
    taxable_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    cgst_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    sgst_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    igst_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    round_off = Column(Numeric(19, 4), nullable=False, default=0.0000)
    grand_total = Column(Numeric(19, 4), nullable=False, default=0.0000)
    currency = Column(String(3), nullable=False, default='INR')
    status = Column(String(30), nullable=False, default='DRAFT')
    notes = Column(Text, nullable=True)
    terms = Column(Text, nullable=True)
    created_by = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    finalized_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint('business_id', 'invoice_number', name='uix_bus_inv_num'),
        {'mysql_charset': 'utf8mb4'}
    )

    items = relationship('InvoiceItem', back_populates='invoice', cascade='all, delete-orphan')
    customer_snapshot = relationship('InvoiceCustomerSnapshot', uselist=False, back_populates='invoice', cascade='all, delete-orphan')
    seller_snapshot = relationship('InvoiceSellerSnapshot', uselist=False, back_populates='invoice', cascade='all, delete-orphan')
    business = relationship('Business')
    customer = relationship('Customer')
    creator = relationship('User')

class InvoiceItem(Base):
    __tablename__ = 'invoice_items'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id = Column(BigInteger, ForeignKey('invoices.id'), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=True)
    line_number = Column(Integer, nullable=False)
    description = Column(String(500), nullable=False)
    cat = Column(String(50), nullable=True)
    hsn_sac = Column(String(20), nullable=True)
    quantity = Column(Numeric(19, 4), nullable=False)
    unit = Column(String(30), nullable=True)
    rate = Column(Numeric(19, 4), nullable=False)
    discount_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    taxable_amount = Column(Numeric(19, 4), nullable=False)
    gst_rate = Column(Numeric(5, 2), nullable=False)
    cgst_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    sgst_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    igst_amount = Column(Numeric(19, 4), nullable=False, default=0.0000)
    total_amount = Column(Numeric(19, 4), nullable=False)

    __table_args__ = {'mysql_charset': 'utf8mb4'}

    invoice = relationship('Invoice', back_populates='items')
    product = relationship('Product')

class InvoiceCustomerSnapshot(Base):
    __tablename__ = 'invoice_customer_snapshots'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id = Column(BigInteger, ForeignKey('invoices.id'), unique=True, nullable=False)
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

    __table_args__ = {'mysql_charset': 'utf8mb4'}

    invoice = relationship('Invoice', back_populates='customer_snapshot')

class InvoiceSellerSnapshot(Base):
    __tablename__ = 'invoice_seller_snapshots'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id = Column(BigInteger, ForeignKey('invoices.id'), unique=True, nullable=False)
    legal_name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    gstin = Column(String(15), nullable=True)
    pan = Column(String(10), nullable=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    state_code = Column(String(5), nullable=True)
    pincode = Column(String(10), nullable=True)
    licence_number = Column(String(100), nullable=True)
    logo_url = Column(String(500), nullable=True)
    bank_name = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_ifsc = Column(String(20), nullable=True)
    bank_branch = Column(String(255), nullable=True)
    signatory_name = Column(String(255), nullable=True)

    __table_args__ = {'mysql_charset': 'utf8mb4'}

    invoice = relationship('Invoice', back_populates='seller_snapshot')
