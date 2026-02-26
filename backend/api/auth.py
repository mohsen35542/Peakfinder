"""
API احراز هویت
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """ثبت‌نام کاربر جدید با ۳ روز رایگان"""
    # TODO: ایجاد کاربر در دیتابیس
    return {
        "message": "ثبت‌نام با موفقیت انجام شد",
        "trial_days": 3,
        "trial_ends": (datetime.utcnow() + timedelta(days=3)).isoformat()
    }

@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """ورود کاربر"""
    # TODO: بررسی اعتبار و ایجاد توکن
    return {
        "access_token": "sample_token",
        "expires_in": 3600
    }

@router.get("/me")
async def get_current_user():
    """اطلاعات کاربر فعلی"""
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "trial_ends": (datetime.utcnow() + timedelta(days=2)).isoformat()
    }