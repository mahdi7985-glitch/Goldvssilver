import logging
from src.data_fetcher import get_all_data
from src.analyzer import analyze
from src.decision_engine import calculate_score
from src.risk_manager import calculate_risk
from src.database import init_db, save_signal, get_last_signal
from bots.telegram_bot import send_telegram_signal
from bots.bale_bot import send_bale_signal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("🚀 ربات تحلیل طلا و نقره شروع به کار کرد...")
    
    try:
        # ۱. دریافت داده
        logging.info("📥 در حال دریافت داده از TGJU...")
        data = get_all_data()
        
        if not data:
            logging.warning("⚠️ داده‌ای دریافت نشد")
            return
        
        # ۲. تحلیل
        logging.info("🔍 در حال تحلیل داده...")
        analysis = analyze(data)
        
        # ۳. محاسبه امتیاز
        score, reasons = calculate_score(analysis)
        logging.info(f"📊 امتیاز سیستم: {score}")
        
        # ۴. مدیریت ریسک
        risk = calculate_risk(data['silver_999'], analysis['atr'])
        
        # ۵. ارسال سیگنال (همیشه در هر اجرا)
        logging.info("📤 ارسال سیگنال...")
        
        # ارسال به تلگرام
        send_telegram_signal(score, reasons, data, risk)
        
        # ارسال به بله
        send_bale_signal(score, reasons, data, risk)
        
        logging.info("✅ اجرای ربات با موفقیت کامل شد.")
        
    except Exception as e:
        logging.error(f"❌ خطا در اجرای ربات: {e}")

if __name__ == "__main__":
    main()
