import os
from dotenv import load_dotenv

load_dotenv()

# توکن‌های ربات‌ها
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))

# تنظیمات تحلیل
ARBITRAGE_THRESHOLD = 5.0  # درصد حباب برای سیگنال
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
