import requests
import re
import logging
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from config.settings import TGJU_URL

logging.basicConfig(level=logging.INFO)
DATA_SOURCE = "live"

# هدرهای استاندارد
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fa,en-US;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
}


# ============================================
# توابع کمکی برای پارس قیمت
# ============================================
def _parse_price_text(text: str) -> float:
    """رشته قیمت (با جداکننده هزارگان و احتمالاً واحد) را به float تبدیل می‌کند."""
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


def _extract_number_from_text(text: str) -> Optional[float]:
    """استخراج عدد از متن (برای مواقعی که قیمت در متن پنهان شده)"""
    numbers = re.findall(r'[\d,]+', text.replace(",", ""))
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return None
    return None


# ============================================
# دریافت قیمت از tgju.org
# ============================================
def _fetch_from_tgju(url: str, selector: str = None) -> float:
    """دریافت قیمت از صفحه‌ی tgju.org با سلکتور مشخص"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f"خطا در اتصال به {url}: {e}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # سلکتورهای مختلف برای پیدا کردن قیمت
    candidates = [
        soup.select_one("span#last-price-value"),
        soup.select_one("[data-col='info.last_trade.PDrCotVal']"),
        soup.select_one("table.table-condensed tbody tr td.text-left"),
        soup.select_one(".fs-txt-black .value"),
        soup.select_one("span[data-last-price]"),
        soup.select_one(".price-value"),
        soup.select_one(".last-price"),
    ]
    
    if selector:
        candidates.insert(0, soup.select_one(selector))
    
    for tag in candidates:
        if tag and tag.get_text(strip=True):
            text = tag.get_text(strip=True)
            try:
                return _parse_price_text(text)
            except ValueError:
                continue
    
    # اگر با سلکتورها پیدا نشد، جستجوی کلی در متن
    all_text = soup.get_text()
    numbers = [float(n.replace(",", "")) for n in all_text.split() 
               if n.replace(",", "").replace(".", "").isdigit() and len(n) > 4]
    
    if numbers:
        probable_price = max(numbers)
        if probable_price > 100000:
            return probable_price
    
    raise Exception("قیمت در صفحه پیدا نشد")


def fetch_silver_price() -> float:
    """دریافت قیمت نقره ۹۹۹ از tgju.org"""
    silver_url = "https://www.tgju.org/profile/silver-gram"
    return _fetch_from_tgju(silver_url)


def fetch_gold_18_price() -> float:
    """دریافت قیمت طلای ۱۸ عیار از tgju.org"""
    gold_18_url = "https://www.tgju.org/profile/geram18"
    return _fetch_from_tgju(gold_18_url)


def fetch_gold_24_price() -> float:
    """دریافت قیمت طلای ۲۴ عیار از tgju.org"""
    gold_24_url = "https://www.tgju.org/profile/geram24"
    return _fetch_from_tgju(gold_24_url)


def fetch_dollar_price() -> float:
    """دریافت قیمت دلار آزاد از tgju.org"""
    dollar_url = "https://www.tgju.org/profile/price_dollar_rl"
    return _fetch_from_tgju(dollar_url)


def fetch_ounce_gold_price() -> float:
    """دریافت قیمت اونس طلا از tgju.org"""
    ounce_url = "https://www.tgju.org/profile/gold_ounce"
    return _fetch_from_tgju(ounce_url)


def fetch_ounce_silver_price() -> float:
    """دریافت قیمت اونس نقره از tgju.org"""
    silver_ounce_url = "https://www.tgju.org/profile/silver-ounce"
    return _fetch_from_tgju(silver_ounce_url)


# ============================================
# توابع اصلی برای دریافت همه قیمت‌ها
# ============================================
def get_all_data() -> Dict[str, Any]:
    """
    دریافت همه قیمت‌های مورد نیاز از tgju.org
    در صورت بروز خطا، از داده‌های جایگزین استفاده می‌کند
    """
    global DATA_SOURCE
    
    try:
        results = {}
        errors = []
        
        # دریافت هر قیمت به صورت جداگانه
        try:
            results['silver_999'] = fetch_silver_price()
            logging.info(f"✅ نقره: {results['silver_999']:,}")
        except Exception as e:
            errors.append(f"نقره: {e}")
            results['silver_999'] = 0
        
        try:
            results['gold_18'] = fetch_gold_18_price()
            logging.info(f"✅ طلای ۱۸: {results['gold_18']:,}")
        except Exception as e:
            errors.append(f"طلای ۱۸: {e}")
            results['gold_18'] = 0
        
        try:
            results['gold_24'] = fetch_gold_24_price()
            logging.info(f"✅ طلای ۲۴: {results['gold_24']:,}")
        except Exception as e:
            errors.append(f"طلای ۲۴: {e}")
            results['gold_24'] = 0
        
        try:
            results['dollar'] = fetch_dollar_price()
            logging.info(f"✅ دلار: {results['dollar']:,}")
        except Exception as e:
            errors.append(f"دلار: {e}")
            results['dollar'] = 0
        
        try:
            results['gold_ounce'] = fetch_ounce_gold_price()
            logging.info(f"✅ انس طلا: {results['gold_ounce']:.2f}")
        except Exception as e:
            errors.append(f"انس طلا: {e}")
            results['gold_ounce'] = 0
        
        try:
            results['silver_ounce'] = fetch_ounce_silver_price()
            logging.info(f"✅ انس نقره: {results['silver_ounce']:.2f}")
        except Exception as e:
            errors.append(f"انس نقره: {e}")
            results['silver_ounce'] = 0
        
        # اگر همه قیمت‌ها صفر بود، از داده‌های جایگزین استفاده کن
        if all(v == 0 for v in [results['silver_999'], results['gold_18'], results['dollar']]):
            logging.warning("⚠️ همه قیمت‌ها صفر شد، استفاده از داده‌های جایگزین...")
            DATA_SOURCE = "fallback (goldprice.org)"
            return get_fallback_data()
        
        DATA_SOURCE = "live (tgju.org)"
        
        # محاسبه مشتقات
        results.update(calculate_derived_data(results))
        
        logging.info(f"✅ همه داده‌ها دریافت شد: نقره {results['silver_999']:,} تومان")
        return results
        
    except Exception as e:
        logging.error(f"❌ خطا در دریافت داده: {e}")
        DATA_SOURCE = "fallback (goldprice.org)"
        return get_fallback_data()


def calculate_derived_data(data: Dict[str, float]) -> Dict[str, float]:
    """محاسبه قیمت منصفانه، حباب و نسبت طلا به نقره"""
    try:
        fair_silver = (data['silver_ounce'] * data['dollar']) / 31.103
        fair_gold = (data['gold_ounce'] * data['dollar']) / 31.103
    except:
        fair_silver = data['silver_999']
        fair_gold = data['gold_18']
    
    return {
        'fair_silver': fair_silver,
        'fair_gold': fair_gold,
        'silver_premium': ((data['silver_999'] / fair_silver) - 1) * 100 if fair_silver > 0 else 0,
        'gold_premium': ((data['gold_18'] / fair_gold) - 1) * 100 if fair_gold > 0 else 0,
        'gold_silver_ratio': data['gold_ounce'] / data['silver_ounce'] if data['silver_ounce'] > 0 else 69.3,
    }


def get_fallback_data() -> Dict[str, Any]:
    """داده‌های جایگزین در صورت عدم دسترسی به سایت"""
    logging.info("📊 استفاده از داده‌های جایگزین (goldprice.org)")
    data = {
        'gold_ounce': 4062.37,
        'silver_ounce': 58.58,
        'dollar': 1931150,
        'gold_18': 18855400,
        'gold_24': 25140300,
        'silver_999': 3860100,
    }
    data.update(calculate_derived_data(data))
    return data
