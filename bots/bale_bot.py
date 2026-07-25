import requests
import logging
import time
from config.settings import BALE_TOKEN, BALE_CHAT_ID
import jdatetime
from datetime import datetime, timezone
from src.data_fetcher import DATA_SOURCE  # وارد کردن وضعیت منبع داده

logger = logging.getLogger(__name__)

def send_bale_signal(score, reasons, data, risk_silver, risk_gold, max_retries=3):
    if not BALE_TOKEN or not BALE_CHAT_ID:
        logger.warning("⚠️ توکن یا آیدی تنظیم نشده")
        return False

    # ساعت ایران
    utc_now = datetime.now(timezone.utc)
    iran_now = utc_now + jdatetime.timedelta(hours=3, minutes=30)
    now = jdatetime.datetime.fromgregorian(datetime=iran_now)
    
    weekday_map = {'Saturday': 'شنبه', 'Sunday': 'یکشنبه', 'Monday': 'دوشنبه',
                   'Tuesday': 'سه‌شنبه', 'Wednesday': 'چهارشنبه', 'Thursday': 'پنجشنبه', 'Friday': 'جمعه'}
    month_map = {'Farvardin': 'فروردین', 'Ordibehesht': 'اردیبهشت', 'Khordad': 'خرداد',
                 'Tir': 'تیر', 'Mordad': 'مرداد', 'Shahrivar': 'شهریور',
                 'Mehr': 'مهر', 'Aban': 'آبان', 'Azar': 'آذر',
                 'Dey': 'دی', 'Bahman': 'بهمن', 'Esfand': 'اسفند'}
    
    persian_date = f"{weekday_map.get(now.strftime('%A'), '')} {now.strftime('%d')} {month_map.get(now.strftime('%B'), '')} {now.strftime('%Y')} - ساعت {now.strftime('%H:%M')}"

    # اصلاح قیمت دلار
    dollar_corrected = data['dollar'] / 10

    # تعیین وضعیت کلی
    if score >= 70:
        status_emoji = "🔥"
        status_text = "خرید قوی"
        advice = "فرصت عالی برای خرید"
    elif score >= 50:
        status_emoji = "📈"
        status_text = "خرید ملایم"
        advice = "احتمال رشد وجود دارد"
    elif score >= 30:
        status_emoji = "⏸️"
        status_text = "نگهداری"
        advice = "فعلاً دست نگه دار"
    elif score >= 10:
        status_emoji = "📉"
        status_text = "فروش ملایم"
        advice = "احتمال ریزش وجود دارد"
    else:
        status_emoji = "💀"
        status_text = "فروش قوی"
        advice = "ریسک بالاست، احتیاط کن"

    # توضیح کامل "چرا این تصمیم؟"
    decision_explanation = "".join([
        "دوست من، این تصمیم بر اساس چند تا نشانه‌ی مهم گرفته شده:\n\n",
        chr(10).join(['🔸 ' + r for r in reasons]),
        "\n\nوقتی اینا رو کنار هم می‌ذاریم، به این نتیجه می‌رسیم که الان شرایط برای ",
        "معامله‌ی نقره مناسب‌تر شده. البته همیشه یادت باشه که بازار پیش‌بینی‌پذیر نیست ",
        "و این تحلیل فقط یه راهنمایی‌ست. 😊"
    ])

    # توضیح کامل حباب قیمتی
    premium_explanation = (
        f"نقره: {data['silver_premium']:+.1f}% - "
        f"{'یعنی نقره الان ارزون‌تر از ارزش جهانی‌ش هست' if data['silver_premium'] < 0 else 'یعنی نقره الان گرون‌تر از ارزش جهانی‌ش هست'}.\n"
        f"طلا: {data['gold_premium']:+.1f}% - "
        f"{'یعنی طلا الان ارزون‌تر از ارزش جهانی‌ش هست' if data['gold_premium'] < 0 else 'یعنی طلا الان گرون‌تر از ارزش جهانی‌ش هست'}.\n"
        "(عدد منفی یعنی کالا نسبت به قیمت جهانی‌اش با تخفیف فروخته می‌شه و عدد مثبت یعنی با حباب.)"
    )

    # اطلاع از منبع داده
    data_source_text = f"📡 منبع داده: {DATA_SOURCE}"
    if "fallback" in DATA_SOURCE:
        data_source_text += "\n⚠️ توجه: داده‌های لحظه‌ای در دسترس نبود. قیمت‌ها بر اساس داده‌های جایگزین نمایش داده می‌شوند و ممکن است با بازار واقعی تفاوت داشته باشند."

    # ساخت پیام (بدون Markdown برای بله)
    message = f"""
سلام! 👋

{status_emoji} تحلیل بازار نقره
📅 {persian_date}

{data_source_text}

---
وضعیت کلی: {status_text} - {advice}
امتیاز سیستم: {score} از ۱۰۰

---
{decision_explanation}

---
حباب قیمتی (ارزش منصفانه در برابر قیمت بازار):
{premium_explanation}

---
قیمت‌های لحظه‌ای (از سایت tgju.org):
نقره ۹۹۹: {data['silver_999']:,.0f} تومان
طلای ۱۸ عیار: {data['gold_18']:,.0f} تومان
طلای ۲۴ عیار: {data['gold_24']:,.0f} تومان
دلار: {dollar_corrected:,.0f} تومان
انس طلا: {data['gold_ounce']:.2f} دلار
انس نقره: {data['silver_ounce']:.2f} دلار
نسبت طلا به نقره: {data['gold_silver_ratio']:.1f}

---
معامله نقره:
{risk_silver['suggestion']}
حد ضرر: {risk_silver['stop_loss']:,.0f} تومان
حد سود: {risk_silver['take_profit']:,.0f} تومان
حجم پیشنهادی: {risk_silver['quantity']} گرم
سود خالص: {risk_silver['net_profit']:.1f}%

{risk_silver['explanation']}

---
معامله طلا:
{risk_gold['suggestion']}
حد ضرر: {risk_gold['stop_loss']:,.0f} تومان
حد سود: {risk_gold['take_profit']:,.0f} تومان
حجم پیشنهادی: {risk_gold['quantity']} گرم
سود خالص: {risk_gold['net_profit']:.1f}%

{risk_gold['explanation']}
"""

    # ارسال با Retry
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage",
                json={'chat_id': BALE_CHAT_ID, 'text': message},
                timeout=15
            )
            if response.status_code == 200:
                logger.info("✅ پیام به بله ارسال شد")
                return True
            elif response.status_code == 503:
                logger.warning(f"⚠️ خطای ۵۰۳، تلاش {attempt+1}/{max_retries}")
                time.sleep(5)
        except Exception as e:
            logger.error(f"❌ خطا: {e}")
            time.sleep(5)
    
    logger.error("❌ ارسال به بله پس از ۳ تلاش ناموفق بود.")
    return False
