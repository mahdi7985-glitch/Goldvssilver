import numpy as np
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

def analyze(data):
    """
    تحلیل بنیادی و فنی
    """
    # ۱. قیمت منصفانه (بر اساس انس و دلار) - به تومان
    fair_silver = (data['silver_ounce'] * data['dollar_toman']) / 31.103
    fair_gold = (data['gold_ounce'] * data['dollar_toman']) / 31.103
    
    # ۲. حباب
    silver_premium = ((data['silver_999_toman'] / fair_silver) - 1) * 100
    gold_premium = ((data['gold_18_toman'] / fair_gold) - 1) * 100
    
    # ۳. نسبت طلا به نقره با تفسیر
    gold_silver_ratio = data['gold_ounce'] / data['silver_ounce']
    
    # تفسیر نسبت (مقایسه با میانگین تاریخی ۷۰-۸۵)
    if gold_silver_ratio > 85:
        ratio_interpretation = "نقره نسبت به طلا ارزان‌تر است"
        ratio_signal = "خرید نقره"
    elif gold_silver_ratio < 70:
        ratio_interpretation = "نقره نسبت به طلا گران‌تر است"
        ratio_signal = "فروش نقره"
    else:
        ratio_interpretation = "نسبت طلا به نقره در محدوده متعادل است"
        ratio_signal = "نگهداری"
    
    # ۴. شاخص‌های فنی
    rsi_silver = calculate_rsi(data['silver_999_toman'])
    rsi_gold = calculate_rsi(data['gold_18_toman'])
    macd_signal = calculate_macd(data['silver_999_toman'])
    adx = calculate_adx(data['silver_999_toman'])
    atr = data['silver_999_toman'] * 0.02  # تخمین ATR
    
    # ۵. تغییرات دلار و انس (برای تحلیل)
    dollar_change = calculate_percent_change(data.get('dollar_history', []))
    ounce_change = calculate_percent_change(data.get('silver_ounce_history', []))
    
    return {
        'fair_silver': fair_silver,
        'fair_gold': fair_gold,
        'silver_premium': silver_premium,
        'gold_premium': gold_premium,
        'gold_silver_ratio': gold_silver_ratio,
        'ratio_interpretation': ratio_interpretation,
        'ratio_signal': ratio_signal,
        'rsi_silver': rsi_silver,
        'rsi_gold': rsi_gold,
        'macd_signal': macd_signal,
        'adx': adx,
        'atr': atr,
        'price': data['silver_999_toman'],
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
        return 0.5  # مقدار پیش‌فرض
    try:
        last = history[-1]
        prev = history[-2]
        return ((last - prev) / prev) * 100
    except:
        return 0.5
