from __future__ import annotations

from typing import Optional
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class InvoiceItemCreate(BaseModel):
    product_id: Optional[int] = None
    description: str = Field(..., max_length=500)
    cat: Optional[str] = Field(None, max_length=50)
    hsn_sac: Optional[str] = Field(None, max_length=20)
    quantity: Decimal = Field(..., gt=0)
    unit: Optional[str] = Field(None, max_length=30)
    rate: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Field(Decimal('0.00'), ge=0)
    gst_rate: Decimal = Field(..., ge=0, le=100)

class InvoiceItemResponse(InvoiceItemCreate):
    id: int
    invoice_id: int
    line_number: int
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    total_amount: Decimal

    model_config = ConfigDict(from_attributes=True)

class InvoiceCreate(BaseModel):
    customer_id: Optional[int] = None
    invoice_date: date
    tax_mode: str = Field(..., pattern="^(CGST_SGST|IGST)$")
    reverse_charge: bool = False
    notes: Optional[str] = None
    terms: Optional[str] = None
    items: list[InvoiceItemCreate] = Field(..., min_length=1)

class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    invoice_date: Optional[date] = None
    tax_mode: Optional[str] = Field(None, pattern="^(CGST_SGST|IGST)$")
    reverse_charge: Optional[bool] = None
    notes: Optional[str] = None
    terms: Optional[str] = None
    items: Optional[list[InvoiceItemCreate]] = Field(None, min_length=1)

class InvoiceCustomerSnapshotResponse(BaseModel):
    id: int
    invoice_id: int
    customer_name: str
    gstin: Optional[str] = None
    licence_number: Optional[str] = None
    pan_number: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    pincode: Optional[str] = None
    place_of_supply: Optional[str] = None
    taxpayer_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceSellerSnapshotResponse(BaseModel):
    id: int
    invoice_id: int
    legal_name: str
    trade_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    state_code: Optional[str] = None
    pincode: Optional[str] = None
    licence_number: Optional[str] = None
    logo_url: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_ifsc: Optional[str] = None
    bank_branch: Optional[str] = None
    signatory_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

from app.schemas.customer import CustomerResponse
from app.schemas.business import BusinessResponse

class InvoiceResponse(BaseModel):
    id: int
    business_id: int
    customer_id: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: date
    tax_mode: str
    reverse_charge: bool
    subtotal: Decimal
    taxable_amount: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    round_off: Decimal
    grand_total: Decimal
    currency: str
    status: str
    notes: Optional[str] = None
    terms: Optional[str] = None
    created_by: int
    finalized_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    items: list[InvoiceItemResponse]
    customer_snapshot: Optional[InvoiceCustomerSnapshotResponse] = None
    seller_snapshot: Optional[InvoiceSellerSnapshotResponse] = None
    customer: Optional[CustomerResponse] = None
    business: Optional[BusinessResponse] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    limit: int
    pages: int
