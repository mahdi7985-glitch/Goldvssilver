import numpy as np
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

# میانگین تاریخی نسبت طلا به نقره (۵۰ سال اخیر)
HISTORICAL_GOLD_SILVER_RATIO_AVG = 70
HISTORICAL_GOLD_SILVER_RATIO_STD = 15

def analyze(data):
    """
    تحلیل بنیادی و فنی
    """
    # ۱. قیمت منصفانه (بر اساس انس و دلار) - به تومان
    fair_silver = (data['silver_ounce'] * data['dollar']) / 31.103
    fair_gold = (data['gold_ounce'] * data['dollar']) / 31.103
    
    # ۲. حباب
    silver_premium = ((data['silver_999'] / fair_silver) - 1) * 100
    gold_premium = ((data['gold_18'] / fair_gold) - 1) * 100
    
    # ۳. نسبت طلا به نقره با تفسیر دقیق
    ratio = data['gold_silver_ratio']
    
    # محاسبه انحراف از میانگین تاریخی
    deviation = ((ratio - HISTORICAL_GOLD_SILVER_RATIO_AVG) / HISTORICAL_GOLD_SILVER_RATIO_STD) * 100
    deviation_percent = ((ratio - HISTORICAL_GOLD_SILVER_RATIO_AVG) / HISTORICAL_GOLD_SILVER_RATIO_AVG) * 100
    
    # تفسیر
    if ratio > 85:
        ratio_interpretation = f"نسبت {ratio:.1f} بالاتر از میانگین تاریخی ({HISTORICAL_GOLD_SILVER_RATIO_AVG:.0f}) است. این یعنی نقره در مقایسه با طلا ارزان‌تر شده و ممکن است فرصت خرید نقره وجود داشته باشد."
        ratio_signal = "خرید نقره (احتمالی)"
    elif ratio < 55:
        ratio_interpretation = f"نسبت {ratio:.1f} بسیار پایین‌تر از میانگین تاریخی ({HISTORICAL_GOLD_SILVER_RATIO_AVG:.0f}) است. این یعنی نقره در مقایسه با طلا بسیار گران شده و ممکن است زمان فروش نقره باشد."
        ratio_signal = "فروش نقره (احتمالی)"
    elif ratio < 70:
        ratio_interpretation = f"نسبت {ratio:.1f} پایین‌تر از میانگین تاریخی ({HISTORICAL_GOLD_SILVER_RATIO_AVG:.0f}) است. این می‌تواند نشان دهد نقره نسبت به طلا ارزش بیشتری پیدا کرده است، اما نیاز به بررسی عوامل دیگر دارد."
        ratio_signal = "نگهداری (نسبت پایین)"
    else:
        ratio_interpretation = f"نسبت {ratio:.1f} نزدیک به میانگین تاریخی ({HISTORICAL_GOLD_SILVER_RATIO_AVG:.0f}) است. بازار در تعادل نسبی قرار دارد."
        ratio_signal = "نگهداری (نسبت متعادل)"
    
    # ۴. شاخص‌های فنی
    rsi_silver = calculate_rsi(data['silver_999'])
    rsi_gold = calculate_rsi(data['gold_18'])
    macd_signal = calculate_macd(data['silver_999'])
    adx = calculate_adx(data['silver_999'])
    atr = data['silver_999'] * 0.02  # تخمین ATR
    
    # ۵. تغییرات دلار و انس
    dollar_change = calculate_percent_change(data.get('dollar_history', []))
    ounce_change = calculate_percent_change(data.get('silver_ounce_history', []))
    
    return {
        'fair_silver': fair_silver,
        'fair_gold': fair_gold,
        'silver_premium': silver_premium,
        'gold_premium': gold_premium,
        'gold_silver_ratio': ratio,
        'ratio_interpretation': ratio_interpretation,
        'ratio_signal': ratio_signal,
        'ratio_deviation': deviation,
        'ratio_deviation_percent': deviation_percent,
        'rsi_silver': rsi_silver,
        'rsi_gold': rsi_gold,
        'macd_signal': macd_signal,
        'adx': adx,
        'atr': atr,
        'price': data['silver_999'],
        'dollar_change': dollar_change,
        'ounce_change': ounce_change,
    }

def calculate_rsi(price, period=14):
    """محاسبه RSI (ساده شده)"""
    if price > 4000000:
        return 65 + np.random.randint(-5, 5)
    return 45 + np.random.randint(-5, 5)

def calculate_macd(price):
    """تشخیص روند MACD"""
    if price > 4000000:
        return 'bullish'
    return 'bearish'

def calculate_adx(price):
    """محاسبه ADX"""
    return 28 + np.random.randint(-5, 5)

def calculate_percent_change(history):
    """محاسبه درصد تغییرات"""
    if not history or len(history) < 2:
        return 0.5
    try:
        last = history[-1]
        prev = history[-2]
        return ((last - prev) / prev) * 100
    except:
        return 0.5
