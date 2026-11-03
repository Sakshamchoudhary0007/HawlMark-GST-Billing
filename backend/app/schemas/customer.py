from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=255)
    gstin: Optional[str] = Field(None, max_length=15)
    licence_number: Optional[str] = Field(None, max_length=100)
    pan_number: Optional[str] = Field(None, max_length=10)
    mobile: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    state_code: Optional[str] = Field(None, max_length=5)
    pincode: Optional[str] = Field(None, max_length=10)
    place_of_supply: Optional[str] = Field(None, max_length=150)
    taxpayer_type: Optional[str] = Field(None, max_length=50)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = Field(None, min_length=2, max_length=255)
    gstin: Optional[str] = Field(None, max_length=15)
    licence_number: Optional[str] = Field(None, max_length=100)
    pan_number: Optional[str] = Field(None, max_length=10)
    mobile: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=255)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    state_code: Optional[str] = Field(None, max_length=5)
    pincode: Optional[str] = Field(None, max_length=10)
    place_of_supply: Optional[str] = Field(None, max_length=150)
    taxpayer_type: Optional[str] = Field(None, max_length=50)


class CustomerResponse(CustomerBase):
    id: int
    business_id: int
    is_archived: bool
    gst_verification_status: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    limit: int
    pages: int
