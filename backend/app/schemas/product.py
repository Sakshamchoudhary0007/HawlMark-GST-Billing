from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    hsn_sac: Optional[str] = Field(None, max_length=20)
    unit: Optional[str] = Field(None, max_length=30)
    default_rate: Decimal = Field(default=Decimal('0.0000'), ge=0)
    gst_rate: Decimal = Field(default=Decimal('0.00'), ge=0, le=100)
    category: Optional[str] = Field(None, max_length=100)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    sku: Optional[str] = Field(None, max_length=100)
    hsn_sac: Optional[str] = Field(None, max_length=20)
    unit: Optional[str] = Field(None, max_length=30)
    default_rate: Optional[Decimal] = Field(None, ge=0)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    category: Optional[str] = Field(None, max_length=100)

class ProductResponse(ProductBase):
    id: int
    business_id: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    limit: int
    pages: int
