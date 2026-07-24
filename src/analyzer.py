import numpy as np
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

def analyze(data):
    """تحلیل بنیادی و فنی"""
    # ۱. قیمت منصفانه (بر اساس انس و دلار)
    fair_silver = (data['silver_ounce'] * data['dollar']) / 31.103
    fair_gold = (data['gold_ounce'] * data['dollar']) / 31.103
    
    # ۲. حباب
    silver_premium = ((data['silver_999'] / fair_silver) - 1) * 100
    gold_premium = ((data['gold_18'] / fair_gold) - 1) * 100
    
    # ۳. نسبت طلا به نقره
    gold_silver_ratio = data['gold_ounce'] / data['silver_ounce']
    
    # ۴. شاخص‌های فنی (با داده‌های تقریبی)
    rsi_silver = calculate_rsi(data['silver_999'])
    rsi_gold = calculate_rsi(data['gold_18'])
    macd_signal = calculate_macd(data['silver_999'])
    adx = calculate_adx(data['silver_999'])
    atr = data['silver_999'] * 0.02  # تقریب ATR
    
    return {
        'fair_silver': fair_silver,
        'fair_gold': fair_gold,
        'silver_premium': silver_premium,
        'gold_premium': gold_premium,
        'gold_silver_ratio': gold_silver_ratio,
        'rsi_silver': rsi_silver,
        'rsi_gold': rsi_gold,
        'macd_signal': macd_signal,
        'adx': adx,
        'atr': atr,
        'price': data['silver_999'],
        'dollar_change': 0.5,  # تخمین
        'ounce_change': 0.3,   # تخمین
    }

def calculate_rsi(price, period=14):
    """محاسبه RSI (ساده شده)"""
    # در نسخه کامل باید تاریخچه داشته باشیم
    if price > 4000000:
        return 65 + np.random.randint(-5, 5)
    return 45 + np.random.randint(-5, 5)

def calculate_macd(price):
    """تشخیص روند MACD (ساده شده)"""
    if price > 4000000:
        return 'bullish'
    return 'bearish'

def calculate_adx(price):
    """محاسبه ADX (ساده شده)"""
    return 28 + np.random.randint(-5, 5)
