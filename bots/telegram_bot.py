import requests
import logging
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import jdatetime
from datetime import datetime, timezone
from src.data_fetcher import DATA_SOURCE  # وارد کردن وضعیت منبع داده

logger = logging.getLogger(__name__)

def send_telegram_signal(score, reasons, data, risk_silver, risk_gold):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ توکن یا آیدی تنظیم نشده")
        return False

    # ... (محاسبات تاریخ و ساعت مانند قبل) ...

    # اضافه کردن بخش منبع داده به پیام
    data_source_text = f"📡 منبع داده: {DATA_SOURCE}"
    if "fallback" in DATA_SOURCE:
        data_source_text += "\n⚠️ توجه: داده‌های لحظه‌ای در دسترس نبود. قیمت‌ها بر اساس داده‌های جایگزین نمایش داده می‌شوند و ممکن است با بازار واقعی تفاوت داشته باشند."

    # ساخت پیام (با اضافه شدن خط منبع داده)
    message = f"""
سلام! 👋

{status_emoji} تحلیل بازار نقره
📅 {persian_date}

{data_source_text}

---
وضعیت کلی: {status_text} - {advice}
امتیاز سیستم: {score} از ۱۰۰

---
...
"""

    # ارسال پیام
    # ...
