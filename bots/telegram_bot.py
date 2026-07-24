import requests
import logging
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# تنظیم لاگر
logger = logging.getLogger(__name__)

def send_telegram_signal(score, reasons, data, risk):
    """
    ارسال سیگنال به تلگرام با استفاده از Polling
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ توکن تلگرام یا آیدی چت تنظیم نشده")
        return False

    try:
        # تعیین وضعیت
        if score >= 70:
            signal = "🟢 خرید قوی"
            emoji = "🔥"
        elif 50 <= score < 70:
            signal = "🟡 خرید معمولی"
            emoji = "📈"
        elif 30 <= score < 50:
            signal = "⚪ نگهداری (بدون معامله)"
            emoji = "⏸️"
        elif 10 <= score < 30:
            signal = "🟠 فروش معمولی"
            emoji = "📉"
        else:
            signal = "🔴 فروش قوی"
            emoji = "💀"

        # ساخت پیام
        message = f"""
{emoji} *سیگنال معاملاتی*

🎯 *وضعیت:* {signal}
📊 *امتیاز سیستم:* {score}/100

📝 *دلایل تحلیل:*
{chr(10).join(reasons)}

💰 *قیمت‌های کلیدی:*
• نقره ۹۹۹: {data['silver_999']:,.0f} تومان
• طلای ۱۸ عیار: {data['gold_18']:,.0f} تومان
• دلار: {data['dollar']:,.0f} تومان
• انس نقره: {data['silver_ounce']:.2f}
• نسبت طلا به نقره: {data['gold_silver_ratio']:.1f}

🛡️ *مدیریت ریسک:*
• حد ضرر: {risk['stop_loss']:,.0f} تومان
• حد سود: {risk['take_profit']:,.0f} تومان
• سود خالص预估: {risk['net_profit']:.1f}٪
• حجم پیشنهادی: {risk['quantity']} گرم

{"✅ معامله به صرفه است" if risk['is_profitable'] else "❌ معامله نکن (سود کافی نیست)"}

---.
        """

        # ارسال پیام با API تلگرام (بدون Webhook)
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            logger.info("✅ پیام به تلگرام ارسال شد")
            return True
        else:
            logger.error(f"❌ خطا در ارسال به تلگرام: {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ خطای غیرمنتظره در ارسال به تلگرام: {e}")
        return False
