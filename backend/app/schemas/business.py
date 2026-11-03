from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.utils.validators import validate_gstin, validate_pan

class BusinessUpdate(BaseModel):
    legal_name: Optional[str] = Field(None, min_length=2)
    trade_name: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
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
    invoice_prefix: Optional[str] = None
    invoice_terms: Optional[str] = None
    invoice_footer: Optional[str] = None
    signatory_name: Optional[str] = None

    @field_validator("gstin")
    def check_gstin(cls, v):
        if v and not validate_gstin(v):
            raise ValueError("Invalid GSTIN format")
        return v

    @field_validator("pan")
    def check_pan(cls, v):
        if v and not validate_pan(v):
            raise ValueError("Invalid PAN format")
        return v

class BusinessResponse(BaseModel):
    id: int
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
    invoice_prefix: Optional[str] = None
    invoice_terms: Optional[str] = None
    invoice_footer: Optional[str] = None
    signatory_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
