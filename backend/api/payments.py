"""
API پرداخت و اشتراک
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/payments", tags=["payments"])

class PaymentRequest(BaseModel):
    plan: str  # monthly, quarterly, yearly
    currency: str  # USDT, BTC, ETH, BNB, TON

class PaymentResponse(BaseModel):
    payment_id: str
    amount: float
    currency: str
    wallet_address: str
    expires_at: datetime

@router.get("/plans")
async def get_plans():
    """پلن‌های اشتراک"""
    return [
        {
            "id": "monthly",
            "name": "ماهانه",
            "price": 5,
            "currency": "USDT",
            "days": 30,
            "features": ["همه سیگنال‌ها", "اندیکاتور کوانتومی", "پشتیبانی"]
        },
        {
            "id": "quarterly",
            "name": "سه ماهه",
            "price": 12,
            "currency": "USDT",
            "days": 90,
            "features": ["همه امکانات", "۲۰٪ تخفیف"]
        },
        {
            "id": "yearly",
            "name": "سالیانه",
            "price": 40,
            "currency": "USDT",
            "days": 365,
            "features": ["همه امکانات", "۳۳٪ تخفیف", "پشتیبانی ویژه"]
        }
    ]

@router.post("/create", response_model=PaymentResponse)
async def create_payment(request: PaymentRequest):
    """ایجاد درخواست پرداخت"""
    # دریافت آدرس کیف پول از تنظیمات ادمین
    wallet_addresses = {
        "USDT": "TXYZ123...",
        "BTC": "1ABCxyz...",
        "ETH": "0x123..."
    }
    
    return {
        "payment_id": f"pay_{datetime.utcnow().timestamp()}",
        "amount": 5.0 if request.plan == "monthly" else 12.0 if request.plan == "quarterly" else 40.0,
        "currency": request.currency,
        "wallet_address": wallet_addresses.get(request.currency, "TXYZ123..."),
        "expires_at": datetime.utcnow() + timedelta(hours=2)
    }

@router.post("/verify/{payment_id}")
async def verify_payment(payment_id: str):
    """تایید پرداخت"""
    # TODO: بررسی تراکنش در بلاکچین
    return {"message": "پرداخت با موفقیت تایید شد"}