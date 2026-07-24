import requests
import logging
from config.settings import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import jdatetime
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def send_telegram_signal(score, reasons, data, risk_silver, risk_gold):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
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
        status, emoji, advice = "خرید", "🔥", "فرصت عالی برای خرید"
    elif score >= 50:
        status, emoji, advice = "خرید ملایم", "📈", "احتمال رشد وجود دارد"
    elif score >= 30:
        status, emoji, advice = "نگهداری", "⏸️", "فعلاً دست نگه دار"
    elif score >= 10:
        status, emoji, advice = "فروش ملایم", "📉", "احتمال ریزش وجود دارد"
    else:
        status, emoji, advice = "فروش", "💀", "ریسک بالاست، احتیاط کن"

    # ساخت پیام
    message = f"""
سلام! 👋

{emoji} تحلیل بازار طلا و نقره
📅 {persian_date}

---
وضعیت کلی: {status} - {advice}
امتیاز سیستم: {score} از ۱۰۰

---
چرا این تصمیم؟
{chr(10).join(['🔸 ' + r for r in reasons])}

---
حباب قیمتی:
💰 نقره: {data['silver_premium']:+.1f}%
💰 طلا: {data['gold_premium']:+.1f}%
(عدد منفی = ارزان، عدد مثبت = گران)

---
قیمت‌های لحظه‌ای:
💰 نقره ۹۹۹: {data['silver_999']:,.0f} تومان
💰 طلای ۱۸ عیار: {data['gold_18']:,.0f} تومان
💰 طلای ۲۴ عیار: {data['gold_24']:,.0f} تومان
💵 دلار: {dollar_corrected:,.0f} تومان
🌍 انس طلا: {data['gold_ounce']:.2f} دلار
🌍 انس نقره: {data['silver_ounce']:.2f} دلار
📊 نسبت طلا به نقره: {data['gold_silver_ratio']:.1f}

---
پیشنهاد معامله برای نقره:
📦 {risk_silver['suggestion']}
🛑 حد ضرر: {risk_silver['stop_loss']:,.0f} تومان
✅ حد سود: {risk_silver['take_profit']:,.0f} تومان
📊 حجم پیشنهادی: {risk_silver['quantity']} گرم
💰 سود خالص预估: {risk_silver['net_profit']:.1f}%

---
پیشنهاد معامله برای طلا:
📦 {risk_gold['suggestion']}
🛑 حد ضرر: {risk_gold['stop_loss']:,.0f} تومان
✅ حد سود: {risk_gold['take_profit']:,.0f} تومان
📊 حجم پیشنهادی: {risk_gold['quantity']} گرم
💰 سود خالص预估: {risk_gold['net_profit']:.1f}%

---
{"✅ معامله نقره به‌صرفه است." if risk_silver['is_profitable'] else "❌ معامله نقره به‌صرفه نیست."}
{"✅ معامله طلا به‌صرفه است." if risk_gold['is_profitable'] else "❌ معامله طلا به‌صرفه نیست."}
"""

    # ارسال
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}, timeout=15)
        logger.info("✅ پیام به تلگرام ارسال شد")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"❌ خطا: {e}")
        return False
