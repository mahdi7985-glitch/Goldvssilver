import requests
import logging
import time
from config.settings import BALE_TOKEN, BALE_CHAT_ID

logger = logging.getLogger(__name__)

def send_bale_signal(score, reasons, data, risk, max_retries=3):
    """
    ارسال سیگنال به بله با قابلیت Retry
    """
    if not BALE_TOKEN or not BALE_CHAT_ID:
        logger.warning("⚠️ توکن بله یا آیدی چت تنظیم نشده")
        return False

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

    # ساخت پیام (بدون Markdown)
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

---
این یک پیشنهاد تحلیلی است. مسئولیت تصمیم‌گیری با شماست.
    """

    # ارسال با Retry
    for attempt in range(max_retries):
        try:
            url = f"https://tapi.bale.ai/v1/bots/{BALE_TOKEN}/sendMessage"
            payload = {
                'chat_id': BALE_CHAT_ID,
                'text': message
            }

            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                logger.info("✅ پیام به بله ارسال شد")
                return True
            elif response.status_code == 503:
                logger.warning(f"⚠️ سرور بله در دسترس نیست (۵۰۳). تلاش {attempt + 1}/{max_retries}")
                time.sleep(5)  # ۵ ثانیه صبر کن و دوباره تلاش کن
            else:
                logger.error(f"❌ خطا در ارسال به بله: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ Timeout در ارسال به بله. تلاش {attempt + 1}/{max_retries}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"❌ خطای غیرمنتظره در ارسال به بله: {e}")
            return False
    
    logger.error("❌ ارسال پیام به بله پس از ۳ تلاش ناموفق بود.")
    return False
