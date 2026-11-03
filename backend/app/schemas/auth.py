from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    business_name: str = Field(..., min_length=2)
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    business_id: int
    
    class Config:
        from_attributes = True
