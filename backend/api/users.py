"""
API مدیریت کاربران
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

class UserProfile(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    language: str = "en"
    theme: str = "light"

@router.get("/profile")
async def get_profile(user_id: int = 1):
    """پروفایل کاربر"""
    return {
        "id": user_id,
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "language": "en",
        "theme": "light",
        "created_at": datetime.utcnow().isoformat()
    }

@router.put("/profile")
async def update_profile(profile: UserProfile):
    """به‌روزرسانی پروفایل"""
    return {"message": "پروفایل به‌روزرسانی شد"}