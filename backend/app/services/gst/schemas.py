from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Optional

class GSTLookupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gstin: str
    legal_name: str
    trade_name: Optional[str] = None
    taxpayer_type: str
    status: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: str
    state_code: str
    pincode: Optional[str] = None
    is_verified: bool
