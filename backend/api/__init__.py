"""
پکیج API - مسیرهای اصلی برنامه
"""

from fastapi import APIRouter

# ایجاد router اصلی
api_router = APIRouter(prefix="/api/v1")

# import مسیرها
from .auth import router as auth_router
from .users import router as users_router
from .signals import router as signals_router
from .smart_signals import router as smart_signals_router
from .payments import router as payments_router
from .health import router as health_router
from .admin import admin_router

# ثبت مسیرها
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(signals_router)
api_router.include_router(smart_signals_router)
api_router.include_router(payments_router)
api_router.include_router(health_router)
api_router.include_router(admin_router)