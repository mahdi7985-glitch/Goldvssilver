import requests
import logging
import time
from config.settings import BALE_TOKEN, BALE_CHAT_ID
import jdatetime
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def send_bale_signal(score, reasons, data, risk_silver, risk_gold, max_retries=3):
    if not BALE_TOKEN or not BALE_CHAT_ID:
        logger.warning("⚠️ توکن یا آیدی بله تنظیم نشده")
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

    # تعیین وضعیت کلی
    status_map = {
        (70, 100): ("🔥", "خرید قوی", "فرصت عالی برای خرید"),
        (50, 69): ("📈", "خرید ملایم", "احتمال رشد وجود دارد"),
        (30, 49): ("⏸️", "نگهداری", "فعلاً دست نگه دار"),
        (10, 29): ("📉", "فروش ملایم", "احتمال ریزش وجود دارد"),
        (-100, 9): ("💀", "فروش قوی", "ریسک بالاست، احتیاط کن")
    }
    
    status_emoji, status_text, advice = "⏸️", "نامشخص", ""
    for (low, high), (emoji, status, adv) in status_map.items():
        if low <= score <= high:
            status_emoji, status_text, advice = emoji, status, adv
            break

    # توضیح دلایل
    if reasons:
        reasons_text = "\n".join(['🔸 ' + r for r in reasons])
    else:
        reasons_text = "🔸 نشانه‌های خاصی پیدا نشد."

    decision_explanation = f"""دوست من، این تصمیم بر اساس چند تا نشانه‌ی مهم گرفته شده:

{reasons_text}"""

    # حباب قیمتی
    def premium_text(value):
        return f"{value:+.1f}% - {'ارزون‌تر از ارزش جهانی' if value < 0 else 'گرون‌تر از ارزش جهانی'}"

    premium_explanation = f"""
نقره: {premium_text(data['silver_premium'])}
طلای ۱۸ عیار: {premium_text(data['gold_18_premium'])}
طلای ۲۴ عیار: {premium_text(data['gold_24_premium'])}
(عدد منفی یعنی کالا نسبت به قیمت جهانی‌اش با تخفیف فروخته می‌شه و عدد مثبت یعنی با حباب.)"""

    # ساخت پیام (بدون Markdown)
    message = f"""
سلام! 👋

{status_emoji} تحلیل بازار نقره
📅 {persian_date}

---
وضعیت کلی: {status_text} - {advice}
امتیاز سیستم: {score} از ۱۰۰

---
{decision_explanation}

---
حباب قیمتی (ارزش منصفانه در برابر قیمت بازار):
{premium_explanation}

---
قیمت‌های لحظه‌ای (تومان):
نقره ۹۹۹: {data['silver_999']:,.0f} تومان
طلای ۱۸ عیار: {data['gold_18']:,.0f} تومان
طلای ۲۴ عیار: {data['gold_24']:,.0f} تومان
دلار: {data['dollar']:,.0f} تومان
انس طلا: {data['gold_ounce']:.2f} دلار
انس نقره: {data['silver_ounce']:.2f} دلار
نسبت طلا به نقره: {data['gold_silver_ratio']:.1f}

---
معامله نقره:
{risk_silver['suggestion']}
حد ضرر: {risk_silver['stop_loss']:,.0f} تومان
حد سود: {risk_silver['take_profit']:,.0f} تومان

{risk_silver['explanation']}

---
معامله طلا:
{risk_gold['suggestion']}
حد ضرر: {risk_gold['stop_loss']:,.0f} تومان
حد سود: {risk_gold['take_profit']:,.0f} تومان

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
