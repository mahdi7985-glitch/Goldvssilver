import os
from dotenv import load_dotenv

load_dotenv()

# توکن‌های ربات‌ها
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BALE_TOKEN = os.getenv("BALE_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BALE_CHAT_ID = os.getenv("BALE_CHAT_ID")

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
MAX_CAPITAL_RISK = 0.10  # ۱۰٪ سرمایه در هر معامله
TRADING_FEE = 0.01  # ۱٪ کارمزد خرید و فروش
MIN_PROFIT_AFTER_FEE = 0.03  # حداقل سود خالص ۳٪

# تنظیمات ارسال پیام
MIN_SCORE_CHANGE = 10
MIN_PRICE_CHANGE = 0.5

# آدرس‌های داده
TGJU_URL = "https://www.tgju.org"
