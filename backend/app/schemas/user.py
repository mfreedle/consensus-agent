import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

# Email validation regex pattern
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


# User schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and v.strip():
            if not EMAIL_REGEX.match(v.strip()):
                raise ValueError('Invalid email format')
        return v.strip() if v else None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and v.strip():
            if not EMAIL_REGEX.match(v.strip()):
                raise ValueError('Invalid email format')
        return v.strip() if v else None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserResponse(UserBase):
    id: int
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenData(BaseModel):
    username: Optional[str] = None
