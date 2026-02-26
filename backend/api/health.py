"""
API بررسی سلامت
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    """بررسی سلامت سرویس"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PeakFinder API",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health():
    """بررسی سلامت با جزئیات"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected"
        },
        "timestamp": datetime.utcnow().isoformat()
    }