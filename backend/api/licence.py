"""
API مدیریت لایسنس
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from ..licence.licence_manager import LicenceManager
from ..licence.hardware_fingerprint import HardwareFingerprint
from ..middleware.auth import get_current_user

router = APIRouter(prefix="/licence", tags=["licence"])
licence_manager = LicenceManager()

class LicenceActivateRequest(BaseModel):
    licence_key: str

class DeviceInfoResponse(BaseModel):
    fingerprint: str
    system: str
    node: str
    machine: str

@router.post("/activate")
async def activate_licence(
    request: LicenceActivateRequest,
    current_user = Depends(get_current_user)
):
    """فعال‌سازی لایسنس برای کاربر فعلی"""
    
    device_info = HardwareFingerprint.get_device_info()
    
    result = await licence_manager.validate_licence(
        request.licence_key,
        device_info
    )
    
    if not result.get("valid"):
        raise HTTPException(status_code=400, detail=result.get("reason"))
    
    return result

@router.get("/my-licence")
async def get_my_licence(current_user = Depends(get_current_user)):
    """دریافت اطلاعات لایسنس کاربر"""
    
    db = SessionLocal()
    try:
        licence = db.query(UserLicence).filter(
            UserLicence.user_id == current_user.id
        ).first()
        
        if not licence:
            return {"has_licence": False}
        
        return {
            "has_licence": True,
            "licence_key": licence.licence_key,
            "type": licence.licence_type,
            "status": licence.status,
            "expires_at": licence.expires_at,
            "registered_devices": len(licence.registered_devices),
            "max_devices": licence.allowed_devices
        }
        
    finally:
        db.close()

@router.get("/device-info")
async def get_device_info():
    """دریافت اطلاعات دستگاه (برای پشتیبانی)"""
    return HardwareFingerprint.get_device_info()

@router.post("/request-new-device")
async def request_new_device(current_user = Depends(get_current_user)):
    """درخواست اضافه کردن دستگاه جدید"""
    
    # TODO: ارسال درخواست به پشتیبانی
    return {
        "message": "درخواست شما ثبت شد. پشتیبانی ظرف ۲۴ ساعت بررسی می‌کند."
    }