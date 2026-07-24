import requests
from config.settings import TELEGRAM_TOKEN, ADMIN_USER_ID
import jdatetime

def send_telegram_signal(score, reasons, data, risk):
    """ارسال سیگنال به تلگرام"""
    if not TELEGRAM_TOKEN or not ADMIN_USER_ID:
        print("⚠️ توکن تلگرام یا آیدی کاربر تنظیم نشده")
        return
    
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
    
    # تاریخ شمسی
    now = jdatetime.datetime.now()
    date_persian = now.strftime("%A %d %B %Y")
    weekday_map = {
        'Saturday': 'شنبه', 'Sunday': 'یکشنبه', 'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه', 'Wednesday': 'چهارشنبه', 'Thursday': 'پنجشنبه',
        'Friday': 'جمعه'
    }
    weekday = weekday_map.get(now.strftime("%A"), "")
    
    # ساخت پیام
    message = f"""
{emoji} *سیگنال معاملاتی - {date_persian}*

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

---
🤝 این یک پیشنهاد تحلیلی است. مسئولیت تصمیم‌گیری با شماست.
    """
    
    # ارسال به تلگرام
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': ADMIN_USER_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ پیام به تلگرام ارسال شد")
        else:
            print(f"❌ خطا در ارسال به تلگرام: {response.text}")
    except Exception as e:
        print(f"❌ خطا: {e}")
