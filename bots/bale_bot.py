import requests
import logging
import time
from config.settings import BALE_TOKEN, BALE_CHAT_ID
import jdatetime

logger = logging.getLogger(__name__)

def send_bale_signal(score, reasons, data, risk, max_retries=3):
    """
    ارسال سیگنال به بله با پیام صمیمی و قابل فهم
    """
    if not BALE_TOKEN or not BALE_CHAT_ID:
        logger.warning("⚠️ توکن بله یا آیدی چت تنظیم نشده")
        return False

    # تاریخ و زمان شمسی
    now = jdatetime.datetime.now()
    weekday_map = {
        'Saturday': 'شنبه', 'Sunday': 'یکشنبه', 'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه', 'Wednesday': 'چهارشنبه', 
        'Thursday': 'پنجشنبه', 'Friday': 'جمعه'
    }
    month_map = {
        'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
        'Tir': 'تیر', 'Mordad': 'مرداد', 'Shahrivar': 'شهریور',
        'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
        'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند'
    }
    
    weekday = weekday_map.get(now.strftime("%A"), "")
    month = month_map.get(now.strftime("%B"), "")
    day = now.strftime("%d")
    year = now.strftime("%Y")
    time = now.strftime("%H:%M")
    
    persian_date = f"{weekday} {day} {month} {year} - ساعت {time}"

    # تعیین وضعیت
    if score >= 70:
        status = "✅ خرید"
        emoji = "🔥"
        advice = "فرصت عالی برای خرید"
    elif 50 <= score < 70:
        status = "📈 خرید ملایم"
        emoji = "📈"
        advice = "احتمال رشد وجود دارد"
    elif 30 <= score < 50:
        status = "⏸️ نگهداری"
        emoji = "⏸️"
        advice = "فعلاً دست نگه دار"
    elif 10 <= score < 30:
        status = "📉 فروش ملایم"
        emoji = "📉"
        advice = "احتمال ریزش وجود دارد"
    else:
        status = "🔴 فروش"
        emoji = "💀"
        advice = "ریسک بالاست، احتیاط کن"

    # ساخت دلیل تحلیل به زبان ساده
    simple_reasons = []
    for r in reasons:
        if "تخفیف" in r:
            simple_reasons.append("🔸 نقره نسبت به قیمت جهانی ارزون‌تر شده")
        elif "حباب" in r:
            simple_reasons.append("🔸 نقره نسبت به قیمت جهانی گرون‌تر شده")
        elif "نسبت طلا به نقره" in r and "بالاست" in r:
            simple_reasons.append("🔸 نسبت طلا به نقره بالاست (نقره در مقایسه با طلا ارزونه)")
        elif "نسبت طلا به نقره" in r and "پایین است" in r:
            simple_reasons.append("🔸 نسبت طلا به نقره پایینه (نقره در مقایسه با طلا گرونه)")
        elif "RSI" in r and "اشباع فروش" in r:
            simple_reasons.append("🔸 شاخص RSI می‌گه نقره بیش از حد فروخته شده و احتمال برگشت داره")
        elif "RSI" in r and "اشباع خرید" in r:
            simple_reasons.append("🔸 شاخص RSI می‌گه نقره بیش از حد خریده شده و احتمال ریزش داره")
        elif "MACD" in r and "صعودی" in r:
            simple_reasons.append("🔸 روند نقره داره صعودی می‌شه")
        elif "MACD" in r and "نزولی" in r:
            simple_reasons.append("🔸 روند نقره داره نزولی می‌شه")
        elif "روند ضعیف" in r:
            simple_reasons.append("🔸 روند بازار ضعیفه، پس بهتره با احتیاط معامله کنی")
        else:
            simple_reasons.append(f"🔸 {r}")

    # ساخت پیام (بدون Markdown)
    message = f"""
سلام! 👋

{emoji} آخرین تحلیل بازار طلا و نقره
📅 {persian_date}

---
وضعیت کلی:
{status} - {advice}
امتیاز سیستم: {score} از ۱۰۰

---
چرا این تصمیم؟

{chr(10).join(simple_reasons)}

---
قیمت‌های الان:
💰 نقره (۹۹۹): {data['silver_999']:,.0f} تومان
💰 طلای ۱۸ عیار: {data['gold_18']:,.0f} تومان
💰 طلای ۲۴ عیار: {data['gold_24']:,.0f} تومان
💵 دلار: {data['dollar']:,.0f} تومان
🌍 انس نقره جهانی: {data['silver_ounce']:.2f} دلار
📊 نسبت طلا به نقره: {data['gold_silver_ratio']:.1f} (هر عدد بالاتر یعنی نقره ارزون‌تره)

---
پیشنهاد مدیریت ریسک:
🛑 حد ضرر: {risk['stop_loss']:,.0f} تومان
✅ حد سود: {risk['take_profit']:,.0f} تومان
📦 حجم پیشنهادی: {risk['quantity']} گرم نقره
💰 سود خالص预估 (بعد از کسر کارمزد): {risk['net_profit']:.1f}%

---
نتیجه‌گیری:
{"✅ این معامله به‌صرفه است و می‌تونه سود خوبی داشته باشه." if risk['is_profitable'] else "❌ این معامله به‌صرفه نیست و پیشنهاد می‌کنم فعلاً معامله نکنی."}

---
🤝 یادآوری: این فقط یک تحلیل هست و تصمیم نهایی با خودت است. همیشه با سرمایه‌ای که می‌تونی از دست بدی، معامله کن.
    """

    # ارسال با Retry
    for attempt in range(max_retries):
        try:
            url = f"https://api.bale.ai/bot{BALE_TOKEN}/sendMessage"
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
                time.sleep(5)
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
