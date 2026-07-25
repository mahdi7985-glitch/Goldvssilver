import requests
import re
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
DATA_SOURCE = "live"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fa,en-US;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
}

def _parse_price_text(text: str) -> float:
    cleaned = (
        text.strip()
        .replace(",", "")
        .replace("٬", "")
        .replace("تومان", "")
        .replace("ریال", "")
        .replace("$", "")
        .replace("دلار", "")
        .strip()
    )
    return float(cleaned)

def _fetch_from_tgju(url: str) -> Optional[float]:
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"خطا در اتصال به {url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    candidates = [
        soup.select_one("span#last-price-value"),
        soup.select_one("[data-col='info.last_trade.PDrCotVal']"),
        soup.select_one("table.table-condensed tbody tr td.text-left"),
        soup.select_one(".fs-txt-black .value"),
        soup.select_one("span[data-last-price]"),
        soup.select_one(".price-value"),
        soup.select_one(".last-price"),
    ]
    
    for tag in candidates:
        if tag and tag.get_text(strip=True):
            text = tag.get_text(strip=True)
            try:
                return _parse_price_text(text)
            except ValueError:
                continue
    
    all_text = soup.get_text()
    numbers = [float(n.replace(",", "")) for n in all_text.split() 
               if n.replace(",", "").replace(".", "").isdigit() and len(n) > 4]
    
    if numbers:
        probable_price = max(numbers)
        if probable_price > 100000:
            return probable_price
    
    return None

# ============================================
# توابع دریافت قیمت
# ============================================
def fetch_silver_price():
    url = "https://www.tgju.org/profile/silver_999"
    return _fetch_from_tgju(url)

def fetch_gold_18_price():
    url = "https://www.tgju.org/profile/geram18"
    return _fetch_from_tgju(url)

def fetch_gold_24_price():
    url = "https://www.tgju.org/profile/geram24"
    return _fetch_from_tgju(url)

def fetch_dollar_price():
    url = "https://www.tgju.org/profile/price_dollar_rl"
    return _fetch_from_tgju(url)

def fetch_ounce_gold_price():
    url = "https://www.tgju.org/profile/ons"
    return _fetch_from_tgju(url)

def fetch_ounce_silver_price():
    url = "https://www.tgju.org/profile/silver"
    return _fetch_from_tgju(url)

# ============================================
# محاسبه حباب طلای ۱۸ و ۲۴ عیار
# ============================================
def calculate_gold_premiums(gold_ounce: float, dollar: float, gold_18: float, gold_24: float) -> Dict[str, float]:
    """
    محاسبه حباب طلای ۱۸ و ۲۴ عیار
    """
    # قیمت منصفانه طلای ۲۴ عیار (خالص)
    fair_gold_24 = (gold_ounce * dollar) / 31.103
    
    # قیمت منصفانه طلای ۱۸ عیار (۷۵٪ خلوص)
    fair_gold_18 = fair_gold_24 * 0.75
    
    # حباب طلای ۲۴ عیار
    gold_24_premium = ((gold_24 / fair_gold_24) - 1) * 100 if fair_gold_24 > 0 else 0
    
    # حباب طلای ۱۸ عیار
    gold_18_premium = ((gold_18 / fair_gold_18) - 1) * 100 if fair_gold_18 > 0 else 0
    
    return {
        'fair_gold_24': fair_gold_24,
        'fair_gold_18': fair_gold_18,
        'gold_24_premium': gold_24_premium,
        'gold_18_premium': gold_18_premium,
    }

# ============================================
# تبدیل قیمت از ریال به تومان
# ============================================
def convert_to_toman(value: float) -> float:
    """تبدیل قیمت از ریال به تومان"""
    return value / 10

# ============================================
# تابع اصلی دریافت داده
# ============================================
def get_all_data() -> Dict[str, Any]:
    global DATA_SOURCE
    
    results = {}
    failed_items = []
    
    price_functions = {
        'silver_999': fetch_silver_price,
        'gold_18': fetch_gold_18_price,
        'gold_24': fetch_gold_24_price,
        'dollar': fetch_dollar_price,
        'gold_ounce': fetch_ounce_gold_price,
        'silver_ounce': fetch_ounce_silver_price,
    }
    
    for name, func in price_functions.items():
        try:
            value = func()
            if value is not None and value > 0:
                results[name] = value
                logging.info(f"✅ {name}: {value:,.0f}")
            else:
                results[name] = 0
                failed_items.append(name)
                logging.warning(f"⚠️ {name}: دریافت نشد")
        except Exception as e:
            results[name] = 0
            failed_items.append(name)
            logging.error(f"❌ {name}: {e}")
    
    # بررسی دریافت نقره و طلا
    if results.get('silver_999', 0) == 0:
        DATA_SOURCE = "error"
        raise Exception("⚠️ قیمت نقره دریافت نشد. لطفاً بعداً تلاش کنید.")
    
    if results.get('gold_18', 0) == 0:
        DATA_SOURCE = "error"
        raise Exception("⚠️ قیمت طلای ۱۸ عیار دریافت نشد. لطفاً بعداً تلاش کنید.")
    
    # محاسبه حباب نقره
    try:
        if results.get('silver_ounce', 0) > 0 and results.get('dollar', 0) > 0:
            fair_silver = (results['silver_ounce'] * results['dollar']) / 31.103
        else:
            fair_silver = results['silver_999']
        
        silver_premium = ((results['silver_999'] / fair_silver) - 1) * 100 if fair_silver > 0 else 0
    except:
        fair_silver = results['silver_999']
        silver_premium = 0
    
    # محاسبه حباب طلای ۱۸ و ۲۴ عیار
    gold_premiums = calculate_gold_premiums(
        results['gold_ounce'],
        results['dollar'],
        results['gold_18'],
        results['gold_24']
    )
    
    # نسبت طلا به نقره
    gold_silver_ratio = results['gold_ounce'] / results['silver_ounce'] if results.get('silver_ounce', 0) > 0 else 69.3
    
    # جمع‌آوری نتایج (تبدیل به تومان برای نمایش)
    results.update({
        'fair_silver': fair_silver / 10,  # تبدیل به تومان
        'silver_premium': silver_premium,
        'gold_silver_ratio': gold_silver_ratio,
        'fair_gold_24': gold_premiums['fair_gold_24'] / 10,  # تبدیل به تومان
        'fair_gold_18': gold_premiums['fair_gold_18'] / 10,  # تبدیل به تومان
        'gold_24_premium': gold_premiums['gold_24_premium'],
        'gold_18_premium': gold_premiums['gold_18_premium'],
        # تبدیل قیمت‌های بازار به تومان
        'silver_999_toman': results['silver_999'] / 10,
        'gold_18_toman': results['gold_18'] / 10,
        'gold_24_toman': results['gold_24'] / 10,
        'dollar_toman': results['dollar'] / 10,
    })
    
    DATA_SOURCE = "live (tgju.org)"
    if failed_items:
        DATA_SOURCE = f"live (با خطا در: {', '.join(failed_items)})"
    
    return results
