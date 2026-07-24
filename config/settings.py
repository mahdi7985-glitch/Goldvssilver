import os
from dotenv import load_dotenv

load_dotenv()

# توکن‌های ربات‌ها (مطابق با عنوان‌های Secrets شما)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")

# آیدی عددی کاربران (مطابق با عنوان‌های Secrets شما)
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
if TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)
else:
    TELEGRAM_CHAT_ID = None

BALE_CHAT_ID = os.getenv("BALE_CHAT_ID")
if BALE_CHAT_ID:
    BALE_CHAT_ID = int(BALE_CHAT_ID)
else:
    BALE_CHAT_ID = None

# تنظیمات تحلیل
ARBITRAGE_THRESHOLD = 5.0
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
ADX_THRESHOLD = 25
GOLD_SILVER_RATIO_HIGH = 85
GOLD_SILVER_RATIO_LOW = 70

# تنظیمات مدیریت ریسک
STOP_LOSS_ATR_MULTIPLIER = 1.5
TAKE_PROFIT_ATR_MULTIPLIER = 2.5
MAX_CAPITAL_RISK = 0.10
TRADING_FEE = 0.01
MIN_PROFIT_AFTER_FEE = 0.03

# تنظیمات ارسال پیام
MIN_SCORE_CHANGE = 10
MIN_PRICE_CHANGE = 0.5

# آدرس‌های داده
TGJU_URL = "https://www.tgju.org"
