from config.settings import (
    ARBITRAGE_THRESHOLD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    ADX_THRESHOLD, GOLD_SILVER_RATIO_HIGH, GOLD_SILVER_RATIO_LOW
)

def calculate_score(analysis):
    """سیستم امتیازدهی"""
    score = 0
    reasons = []
    
    # ۱. حباب نقره (۲۰ امتیاز)
    if analysis['silver_premium'] < -ARBITRAGE_THRESHOLD:
        score += 20
        reasons.append("✅ نقره با تخفیف ۵٪+")
    elif analysis['silver_premium'] > ARBITRAGE_THRESHOLD:
        score -= 20
        reasons.append("❌ نقره با حباب ۵٪+")
    
    # ۲. نسبت طلا به نقره (۲۰ امتیاز)
    if analysis['gold_silver_ratio'] > GOLD_SILVER_RATIO_HIGH:
        score += 20
        reasons.append(f"✅ نسبت طلا به نقره {analysis['gold_silver_ratio']:.1f} (نقره ارزان)")
    elif analysis['gold_silver_ratio'] < GOLD_SILVER_RATIO_LOW:
        score -= 20
        reasons.append(f"❌ نسبت طلا به نقره {analysis['gold_silver_ratio']:.1f} (نقره گران)")
    
    # ۳. RSI (۱۵ امتیاز)
    if analysis['rsi_silver'] < RSI_OVERSOLD:
        score += 15
        reasons.append(f"✅ RSI نقره اشباع فروش ({analysis['rsi_silver']:.0f})")
    elif analysis['rsi_silver'] > RSI_OVERBOUGHT:
        score -= 15
        reasons.append(f"❌ RSI نقره اشباع خرید ({analysis['rsi_silver']:.0f})")
    
    # ۴. MACD (۲۵ امتیاز)
    if analysis['macd_signal'] == 'bullish':
        score += 25
        reasons.append("✅ MACD صعودی")
    else:
        score -= 25
        reasons.append("❌ MACD نزولی")
    
    # ۵. فیلتر ADX
    if analysis['adx'] < ADX_THRESHOLD:
        score = min(score, 30)  # محدود کردن امتیاز در روند ضعیف
        reasons.append(f"⚠️ روند ضعیف (ADX={analysis['adx']:.1f})")
    
    return score, reasons
