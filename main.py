import logging
from src.data_fetcher import get_all_data
from src.analyzer import analyze
from src.decision_engine import calculate_score
from src.risk_manager import calculate_risk
from bots.telegram_bot import send_telegram_signal
from bots.bale_bot import send_bale_signal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("🚀 ربات تحلیل طلا و نقره شروع به کار کرد...")
    
    try:
        # ۱. دریافت داده
        data = get_all_data()
        if not data:
            logging.warning("⚠️ داده‌ای دریافت نشد")
            return
        
        # ۲. تحلیل
        analysis = analyze(data)
        score, reasons = calculate_score(analysis)
        logging.info(f"📊 امتیاز سیستم: {score}")
        
        # ۳. مدیریت ریسک برای نقره و طلا
        risk_silver = calculate_risk(data['silver_999'], analysis['atr'], metal_type='silver')
        risk_gold = calculate_risk(data['gold_18'], analysis['atr'], metal_type='gold')
        
        # ۴. ارسال سیگنال
        send_telegram_signal(score, reasons, data, risk_silver, risk_gold)
        send_bale_signal(score, reasons, data, risk_silver, risk_gold)
        
        logging.info("✅ اجرای ربات با موفقیت کامل شد.")
        
    except Exception as e:
        logging.error(f"❌ خطا در اجرای ربات: {e}")

if __name__ == "__main__":
    main()
