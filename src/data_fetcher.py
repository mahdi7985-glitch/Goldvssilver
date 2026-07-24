import requests
import re
import logging
from datetime import datetime
from config.settings import TGJU_URL

logging.basicConfig(level=logging.INFO)

def get_all_data():
    """دریافت همه داده‌های مورد نیاز از TGJU با timeout کمتر"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # کاهش timeout به ۵ ثانیه
        response = requests.get(TGJU_URL, headers=headers, timeout=5)
        html = response.text
        
        # استخراج داده‌ها با regex
        data = {
            'gold_ounce': extract_price(html, r'انس طلا.*?(\d+,\d+\.\d+)'),
            'silver_ounce': extract_price(html, r'انس نقره.*?(\d+,\d+\.\d+)'),
            'dollar': extract_price(html, r'دلار.*?(\d+,\d+,\d+)'),
            'gold_18': extract_price(html, r'طلای ۱۸ عیار.*?(\d+,\d+,\d+)'),
            'gold_24': extract_price(html, r'طلای ۲۴ عیار.*?(\d+,\d+,\d+)'),
            'silver_999': extract_price(html, r'نقره ۹۹۹.*?(\d+,\d+,\d+)'),
        }
        
        # تبدیل به عدد
        for key in data:
            if data[key]:
                data[key] = float(data[key].replace(',', ''))
        
        logging.info(f"✅ داده دریافت شد: نقره {data['silver_999']:,} تومان")
        return data
        
    except requests.exceptions.Timeout:
        logging.warning("⚠️ مهلت دریافت داده به پایان رسید. استفاده از داده‌های آزمایشی...")
        return get_fallback_data()
    except Exception as e:
        logging.error(f"❌ خطا در دریافت داده: {e}")
        return get_fallback_data()

def extract_price(text, pattern):
    """استخراج قیمت از متن با regex"""
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def get_fallback_data():
    """داده‌های آزمایشی در صورت عدم دسترسی به سایت"""
    logging.info("📊 استفاده از داده‌های آزمایشی (Fallback)")
    return {
        'gold_ounce': 4062.37,
        'silver_ounce': 58.58,
        'dollar': 1931150,
        'gold_18': 18855400,
        'gold_24': 25140300,
        'silver_999': 3860100,
    }
