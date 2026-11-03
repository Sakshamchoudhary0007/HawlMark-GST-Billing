from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|staff)$")
    password: str = Field(..., min_length=8)

class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|staff)$")

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserResponse(BaseModel):
    id: int
    business_id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
