from pydantic import EmailStr, field_validator
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v

    @field_validator('password')
    def password_must_be_valid(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    

class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    user_id: Optional[int] = None
