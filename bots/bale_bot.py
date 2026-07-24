import requests
import logging
from config.settings import BALE_TOKEN, BALE_CHAT_ID

# تنظیم لاگر
logger = logging.getLogger(__name__)

def send_bale_signal(score, reasons, data, risk):
    """
    ارسال سیگنال به بله با استفاده از Polling
    """
    if not BALE_TOKEN or not BALE_CHAT_ID:
        logger.warning("⚠️ توکن بله یا آیدی چت تنظیم نشده")
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

        # ساخت پیام (بدون Markdown برای بله)
        message = f"""
{emoji} سیگنال معاملاتی

وضعیت: {signal}
امتیاز سیستم: {score}/100

دلایل تحلیل:
{chr(10).join(reasons)}

قیمت‌های کلیدی:
• نقره ۹۹۹: {data['silver_999']:,.0f} تومان
• طلای ۱۸ عیار: {data['gold_18']:,.0f} تومان
• دلار: {data['dollar']:,.0f} تومان
• انس نقره: {data['silver_ounce']:.2f}
• نسبت طلا به نقره: {data['gold_silver_ratio']:.1f}

مدیریت ریسک:
• حد ضرر: {risk['stop_loss']:,.0f} تومان
• حد سود: {risk['take_profit']:,.0f} تومان
• سود خالص预估: {risk['net_profit']:.1f}%
• حجم پیشنهادی: {risk['quantity']} گرم

{"✅ معامله به صرفه است" if risk['is_profitable'] else "❌ معامله نکن (سود کافی نیست)"}

---.
        """

        # ارسال پیام با API بله (بدون Webhook)
        url = f"https://api.bale.ai/v1/bots/{BALE_TOKEN}/sendMessage"
        payload = {
            'chat_id': BALE_CHAT_ID,
            'text': message
        }

        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            logger.info("✅ پیام به بله ارسال شد")
            return True
        else:
            logger.error(f"❌ خطا در ارسال به بله: {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ خطای غیرمنتظره در ارسال به بله: {e}")
        return False
