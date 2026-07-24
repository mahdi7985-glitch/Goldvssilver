import time
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
    # راه‌اندازی دیتابیس
    init_db()
    logging.info("🚀 ربات تحلیل طلا و نقره شروع به کار کرد...")
    
    last_score = None
    last_price = None
    
    while True:
        try:
            # ۱. دریافت داده
            logging.info("📥 در حال دریافت داده از TGJU...")
            data = get_all_data()
            
            # ۲. تحلیل
            logging.info("🔍 در حال تحلیل داده...")
            analysis = analyze(data)
            
            # ۳. محاسبه امتیاز
            score, reasons = calculate_score(analysis)
            
            # ۴. مدیریت ریسک
            risk = calculate_risk(data['silver_999'], analysis['atr'])
            
            # ۵. بررسی تغییرات
            should_send = False
            if last_score is None:
                should_send = True
            elif abs(score - last_score) >= 10:
                should_send = True
            elif last_price and abs((data['silver_999'] / last_price - 1) * 100) > 0.5:
                should_send = True
            
            if should_send:
                logging.info(f"📊 سیگنال جدید! امتیاز: {score}")
                
                # ذخیره در دیتابیس
                signal_id = save_signal(score, reasons, data, risk)
                
                # ارسال به تلگرام
                send_telegram_signal(score, reasons, data, risk)
                
                # ارسال به بله
                send_bale_signal(score, reasons, data, risk)
                
                last_score = score
                last_price = data['silver_999']
            
            # ۶. انتظار ۵ دقیقه
            logging.info("⏳ انتظار ۵ دقیقه تا بررسی بعدی...")
            time.sleep(300)
            
        except Exception as e:
            logging.error(f"❌ خطا در حلقه اصلی: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
