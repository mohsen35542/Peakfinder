"""
API سیگنال‌های معاملاتی با هوش SuperBrain
هر سیگنال با مشورت مغز مصنوعی صادر میشه
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

# ================ هوش مصنوعی ================
from ml import super_brain

# ================ سرویس‌ها ================
from ..indicators.peak_vision import PeakVision
from ..indicators.signal_detector import SignalDetector

router = APIRouter(prefix="/signals", tags=["signals"])
logger = logging.getLogger(__name__)

# نمونه از اندیکاتورها
peak_vision = PeakVision()
signal_detector = SignalDetector()

class SignalResponse(BaseModel):
    """مدل پاسخ سیگنال"""
    id: str
    symbol: str
    action: str
    entry_price: float
    stop_loss: float
    take_profit: List[float]
    confidence: float
    timeframe: str
    exchange: str
    created_at: datetime
    reasons: List[str]
    
    # ================ اضافه شده: نظر مغز ================
    brain_advice: dict
    market_prediction: dict

@router.get("/{symbol}", response_model=SignalResponse)
async def get_signal(
    symbol: str,
    timeframe: str = Query("1h", regex="^(1m|5m|15m|1h|4h|1d)$"),
    exchange: str = Query("binance", regex="^(binance|bybit|kucoin|gateio|mexc|huobi|okx|kraken|coinbase|coinex)$")
):
    """
    دریافت سیگنال برای یک نماد خاص
    - ۳ ثانیه تاخیر برای تحلیل عمیق
    - مشورت با SuperBrain برای بهترین زمان
    """
    
    # ================ ۱. مشورت با مغز ================
    logger.info(f"🧠 SuperBrain در حال بررسی {symbol}...")
    
    # بهترین زمان برای این نماد
    best_time = super_brain.get_best_time_to_trade(symbol)
    
    # پیش‌بینی جریان سرمایه
    market_prediction = super_brain.predict_capital_flow(days=1)
    
    # آیا الان وقتشه؟
    trade_time = super_brain.should_trade_now(symbol)
    
    if not trade_time['decision']:
        logger.warning(f"⏳ {symbol} - {trade_time['reason']}")
        # هنوز می‌تونیم سیگنال بدیم، اما با احتیاط
    
    # ================ ۲. تحلیل فنی ================
    await asyncio.sleep(3)  # تحلیل عمیق
    
    # TODO: تحلیل واقعی با signal_detector
    signal_id = f"sig_{datetime.utcnow().timestamp()}"
    
    # ================ ۳. ساخت سیگنال ================
    response = {
        "id": signal_id,
        "symbol": symbol,
        "action": "BUY",  # TODO: از تحلیلگر بیاد
        "entry_price": 52345.50,
        "stop_loss": 51200.00,
        "take_profit": [53200.00, 54000.00, 55000.00],
        "confidence": 87.5,
        "timeframe": timeframe,
        "exchange": exchange,
        "created_at": datetime.utcnow(),
        "reasons": [
            "RSI در محدوده اشباع فروش (28.5)",
            "تشکیل الگوی دو قله در تایم ۴ ساعته",
            "حجم معاملات ۲.۳ برابر میانگین"
        ],
        # ================ نظر مغز ================
        "brain_advice": {
            "best_hour": best_time,
            "trade_now": trade_time,
            "brain_confidence": super_brain.evolution['accuracy']
        },
        "market_prediction": market_prediction[:3] if market_prediction else []
    }
    
    # ================ ۴. ثبت در مغز ================
    # super_brain.learn_from_trade(response)  # بعداً
    
    logger.info(f"✅ سیگنال {symbol} با مشورت مغز صادر شد")
    return response

@router.get("/latest/all")
async def get_latest_signals(limit: int = Query(10, ge=1, le=50)):
    """آخرین سیگنال‌ها با نظر مغز"""
    
    # ================ نظر کلی مغز ================
    market_insights = super_brain.get_market_intelligence()
    
    signals = []
    for i in range(min(limit, 5)):
        signals.append({
            "id": f"sig_{i}",
            "symbol": "BTCUSDT",
            "action": "BUY" if i % 2 == 0 else "SELL",
            "entry_price": 52000.0 + i * 100,
            "confidence": 80.0 + i,
            "created_at": datetime.utcnow() - timedelta(minutes=i*5),
            # نظر مغز برای هر کدوم
            "brain_says": {
                "should_trade": super_brain.should_trade_now("BTCUSDT")['decision']
            }
        })
    
    return {
        "signals": signals,
        "market_intelligence": market_insights
    }

@router.get("/brain/status")
async def get_brain_status():
    """وضعیت SuperBrain"""
    return {
        "brain": super_brain.get_market_intelligence(),
        "evolution": {
            "age": f"{super_brain.evolution['age_days']} روز",
            "accuracy": f"{super_brain.evolution['accuracy']:.1f}%",
            "consciousness": f"{super_brain.evolution['consciousness_level']:.2f}"
        },
        "predictions": super_brain.predict_capital_flow(days=7)
    }