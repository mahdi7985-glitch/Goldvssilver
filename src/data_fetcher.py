import requests
import re
import logging
from config.settings import TGJU_URL

logging.basicConfig(level=logging.INFO)

def get_all_data():
    """دریافت همه داده‌های مورد نیاز از TGJU"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(TGJU_URL, headers=headers, timeout=5)
        html = response.text
        
        # استخراج داده‌ها
        gold_ounce = extract_price(html, r'انس طلا.*?(\d+,\d+\.\d+)')
        silver_ounce = extract_price(html, r'انس نقره.*?(\d+,\d+\.\d+)')
        dollar = extract_price(html, r'دلار.*?(\d+,\d+,\d+)')
        gold_18 = extract_price(html, r'طلای ۱۸ عیار.*?(\d+,\d+,\d+)')
        gold_24 = extract_price(html, r'طلای ۲۴ عیار.*?(\d+,\d+,\d+)')
        silver_999 = extract_price(html, r'نقره ۹۹۹.*?(\d+,\d+,\d+)')
        
        # بررسی وجود داده‌ها
        if None in [gold_ounce, silver_ounce, dollar, gold_18, gold_24, silver_999]:
            logging.warning("⚠️ برخی داده‌ها دریافت نشد. استفاده از داده‌های آزمایشی...")
            return get_fallback_data()
        
        # تبدیل به عدد
        data = {
            'gold_ounce': float(gold_ounce.replace(',', '')),
            'silver_ounce': float(silver_ounce.replace(',', '')),
            'dollar': float(dollar.replace(',', '')),
            'gold_18': float(gold_18.replace(',', '')),
            'gold_24': float(gold_24.replace(',', '')),
            'silver_999': float(silver_999.replace(',', '')),
        }
        
        # محاسبه قیمت منصفانه و حباب
        data['fair_silver'] = (data['silver_ounce'] * data['dollar']) / 31.103
        data['fair_gold'] = (data['gold_ounce'] * data['dollar']) / 31.103
        data['silver_premium'] = ((data['silver_999'] / data['fair_silver']) - 1) * 100
        data['gold_premium'] = ((data['gold_18'] / data['fair_gold']) - 1) * 100
        data['gold_silver_ratio'] = data['gold_ounce'] / data['silver_ounce']
        
        logging.info(f"✅ داده دریافت شد: طلا {data['gold_18']:,} - نقره {data['silver_999']:,} تومان")
        return data
        
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
    """داده‌های آزمایشی"""
    logging.info("📊 استفاده از داده‌های آزمایشی (Fallback)")
    data = {
        'gold_ounce': 4062.37,
        'silver_ounce': 58.58,
        'dollar': 1931150,
        'gold_18': 18855400,
        'gold_24': 25140300,
        'silver_999': 3860100,
    }
    data['fair_silver'] = (data['silver_ounce'] * data['dollar']) / 31.103
    data['fair_gold'] = (data['gold_ounce'] * data['dollar']) / 31.103
    data['silver_premium'] = ((data['silver_999'] / data['fair_silver']) - 1) * 100
    data['gold_premium'] = ((data['gold_18'] / data['fair_gold']) - 1) * 100
    data['gold_silver_ratio'] = data['gold_ounce'] / data['silver_ounce']
    return data
