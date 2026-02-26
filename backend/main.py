"""
نقطه ورود اصلی برنامه
PeakFinder Quantum Trading Platform
نسخه نهایی با همه ماژول‌ها و میدلورها
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import logging
import os

# ================ تنظیمات ================
from core.config import settings
from core.database import engine, Base
from core.redis_client import redis_client

# ================ API ================
from api import api_router
from api.admin import admin_router

# ================ Middleware ================
from middleware.security import SecurityMiddleware
from middleware.subscription_check import SubscriptionCheckMiddleware
from middleware.source_protect import SourceProtectMiddleware
from middleware.rate_limiter import RateLimitMiddleware
from middleware.request_id import RequestIDMiddleware
from middleware.logging_middleware import LoggingMiddleware
from middleware.error_handler import ErrorHandlerMiddleware
from middleware.licence_middleware import LicenceMiddleware  # ✅ میدلور لایسنس

# ================ لاگر ================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================ ایجاد اپلیکیشن ================
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "PeakFinder Support",
        "email": "support@peakfinder.app",
        "url": "https://peakfinder.app"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# ================ تنظیم CORS ================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# ================ ترتیب میدلورها (خیلی مهمه) ================
# 1. اول Error Handler (باید اولین باشه)
app.add_middleware(ErrorHandlerMiddleware)

# 2. بعد Request ID
app.add_middleware(RequestIDMiddleware)

# 3. بعد Logging
app.add_middleware(LoggingMiddleware)

# 4. بعد Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    calls=settings.RATE_LIMIT_REQUESTS,
    period=settings.RATE_LIMIT_PERIOD
)

# 5. بعد Source Protect
app.add_middleware(SourceProtectMiddleware)

# 6. بعد Security
app.add_middleware(SecurityMiddleware)

# 7. بعد Licence (قبل از Subscription)
app.add_middleware(
    LicenceMiddleware,
    exclude_paths=[
        "/",
        "/health",
        "/metrics",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/licence/activate",
        "/api/v1/payments/webhook",
        "/docs",
        "/redoc",
        "/openapi.json"
    ],
    max_devices=1,
    max_suspicious=3
)

# 8. آخر Subscription Check
app.add_middleware(SubscriptionCheckMiddleware)

# ================ ثبت مسیرها ================
app.include_router(api_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1/admin")

# ================ مسیرهای عمومی ================

@app.get("/")
async def root():
    """مسیر اصلی - وضعیت سرویس"""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    """بررسی سلامت ساده"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """بررسی سلامت با جزئیات"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # بررسی دیتابیس
    try:
        from core.database import check_db_connection
        db_ok = check_db_connection()
        health_status["services"]["database"] = {
            "status": "healthy" if db_ok else "unhealthy",
            "message": "Connected" if db_ok else "Disconnected"
        }
        if not db_ok:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        health_status["status"] = "degraded"
    
    # بررسی Redis
    try:
        await redis_client.set("health_check", "ok", 5)
        redis_ok = await redis_client.get("health_check") == "ok"
        health_status["services"]["redis"] = {
            "status": "healthy" if redis_ok else "unhealthy",
            "message": "Connected" if redis_ok else "Disconnected"
        }
        if not redis_ok:
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/metrics")
async def get_metrics():
    """متریک‌های Prometheus"""
    from observability.metrics import metrics_collector
    from fastapi.responses import PlainTextResponse
    
    metrics = metrics_collector.get_metrics()
    return PlainTextResponse(metrics)

@app.get("/info")
async def get_info():
    """اطلاعات سیستم"""
    import platform
    import psutil
    
    return {
        "app": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        },
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available
        },
        "features": {
            "quantum_indicator": True,
            "smart_signals": True,
            "multi_exchange": True,
            "licence_control": True
        },
        "exchanges": [
            "binance", "bybit", "kucoin", "gateio", "mexc",
            "huobi", "okx", "kraken", "coinbase", "coinex"
        ],
        "supported_currencies": settings.ACCEPTED_PAYMENT_CURRENCIES,
        "supported_languages": settings.SUPPORTED_LANGUAGES,
        "default_language": settings.DEFAULT_LANGUAGE
    }

# ================ رویدادهای راه‌اندازی ================

@app.on_event("startup")
async def startup_event():
    """عملیات هنگام راه‌اندازی"""
    logger.info("🚀 " + "="*50)
    logger.info(f"🚀 در حال راه‌اندازی {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("🚀 " + "="*50)
    
    # اتصال به Redis
    try:
        await redis_client.connect()
        logger.info("✅ اتصال به Redis برقرار شد")
    except Exception as e:
        logger.error(f"❌ خطا در اتصال به Redis: {e}")
        if settings.ENVIRONMENT == "production":
            raise
    
    # ایجاد جداول دیتابیس (فقط برای توسعه)
    if settings.ENVIRONMENT == "development":
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ جداول دیتابیس ایجاد شدند (حالت توسعه)")
        except Exception as e:
            logger.error(f"❌ خطا در ایجاد جداول: {e}")
    
    # بررسی صرافی‌ها
    try:
        from exchanges.manager import ExchangeManager
        manager = ExchangeManager()
        exchanges = manager.get_all_exchanges()
        logger.info(f"✅ {len(exchanges)} صرافی آماده به کار: {', '.join(exchanges[:5])}...")
    except Exception as e:
        logger.error(f"❌ خطا در راه‌اندازی صرافی‌ها: {e}")
    
    logger.info("✅ راه‌اندازی کامل شد")
    logger.info("🚀 " + "="*50)

@app.on_event("shutdown")
async def shutdown_event():
    """عملیات هنگام خاموش شدن"""
    logger.info("🔄 در حال خاموش شدن...")
    
    # قطع اتصال Redis
    await redis_client.disconnect()
    logger.info("✅ اتصال Redis قطع شد")
    
    # بستن اتصالات دیتابیس
    from core.database import close_db_connections
    await close_db_connections()
    logger.info("✅ اتصالات دیتابیس بسته شد")
    
    logger.info("✅ خاموش شدن کامل شد")

# ================ Exception Handlers ================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """مدیریت خطای 404"""
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": {
                "code": "not_found",
                "message": "مسیر درخواستی یافت نشد",
                "path": request.url.path
            }
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """مدیریت خطای 500"""
    logger.error(f"خطای داخلی سرور: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "internal_server_error",
                "message": "خطای داخلی سرور رخ داده است"
            }
        }
    )

# ================ WebSocket endpoints ================

from fastapi import WebSocket, WebSocketDisconnect
from api.websocket.connection_manager import manager
from api.websocket.live_prices import websocket_prices
from api.websocket.signal_websocket import websocket_signals
from api.websocket.notification_websocket import websocket_notifications
from api.websocket.chart_websocket import websocket_charts

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """اتصال WebSocket عمومی"""
    await websocket_prices(websocket, client_id)

@app.websocket("/ws/prices/{client_id}")
async def websocket_prices_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket قیمت‌های زنده"""
    from api.websocket.live_prices import websocket_prices
    await websocket_prices(websocket, client_id)

@app.websocket("/ws/signals/{client_id}")
async def websocket_signals_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket سیگنال‌های زنده"""
    from api.websocket.signal_websocket import websocket_signals
    await websocket_signals(websocket, client_id)

@app.websocket("/ws/notifications/{client_id}")
async def websocket_notifications_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket نوتیفیکیشن‌ها"""
    from api.websocket.notification_websocket import websocket_notifications
    await websocket_notifications(websocket, client_id)

@app.websocket("/ws/charts/{client_id}")
async def websocket_charts_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket نمودارها"""
    from api.websocket.chart_websocket import websocket_charts
    await websocket_charts(websocket, client_id)

# ================ Static files (در صورت نیاز) ================

from fastapi.staticfiles import StaticFiles
import os

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ================ راه‌اندازی ================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        workers=1  # در production بیشتر کنید
    )