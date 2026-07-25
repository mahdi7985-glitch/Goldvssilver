from config.settings import (
    ARBITRAGE_THRESHOLD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    ADX_THRESHOLD
)

def calculate_score(analysis):
    """
    سیستم امتیازدهی با وزن‌دهی مناسب
    """
    score = 0
    reasons = []
    
    # ۱. حباب نقره (وزن: ۲۰)
    if analysis['silver_premium'] < -ARBITRAGE_THRESHOLD:
        score += 20
        reasons.append("✅ نقره با تخفیف ۵٪+ (ارزش خرید)")
    elif analysis['silver_premium'] > ARBITRAGE_THRESHOLD:
        score -= 20
        reasons.append("❌ نقره با حباب ۵٪+ (ارزش فروش)")
    
    # ۲. نسبت طلا به نقره (وزن: ۱۵) - با تفسیر درست
    ratio = analysis['gold_silver_ratio']
    if ratio > 85:
        score += 15
        reasons.append(f"✅ نسبت طلا به نقره بالا ({ratio:.1f}) → نقره ارزان‌تر از طلا")
    elif ratio < 70:
        score -= 15
        reasons.append(f"❌ نسبت طلا به نقره پایین ({ratio:.1f}) → نقره گران‌تر از طلا")
    else:
        reasons.append(f"➖ نسبت طلا به نقره در محدوده متعادل ({ratio:.1f})")
    
    # ۳. RSI نقره (وزن: ۱۵)
    rsi = analysis['rsi_silver']
    if rsi < RSI_OVERSOLD:
        score += 15
        reasons.append(f"✅ RSI نقره اشباع فروش ({rsi:.0f}) → احتمال رشد")
    elif rsi > RSI_OVERBOUGHT:
        score -= 15
        reasons.append(f"❌ RSI نقره اشباع خرید ({rsi:.0f}) → احتمال ریزش")
    
    # ۴. MACD (وزن: ۲۵)
    if analysis['macd_signal'] == 'bullish':
        score += 25
        reasons.append("✅ MACD صعودی (روند مثبت)")
    else:
        score -= 25
        reasons.append("❌ MACD نزولی (روند منفی)")
    
    # ۵. روند دلار (وزن: ۱۰)
    dollar_change = analysis.get('dollar_change', 0)
    if dollar_change > 0.5:
        score += 10
        reasons.append(f"✅ دلار در حال رشد ({dollar_change:.1f}%)")
    elif dollar_change < -0.5:
        score -= 10
        reasons.append(f"❌ دلار در حال ریزش ({dollar_change:.1f}%)")
    
    # ۶. روند انس نقره (وزن: ۱۰)
    ounce_change = analysis.get('ounce_change', 0)
    if ounce_change > 0.5:
        score += 10
        reasons.append(f"✅ انس نقره در حال رشد ({ounce_change:.1f}%)")
    elif ounce_change < -0.5:
        score -= 10
        reasons.append(f"❌ انس نقره در حال ریزش ({ounce_change:.1f}%)")
    
    # ۷. فیلتر ADX (قدرت روند)
    adx = analysis.get('adx', 0)
    if adx < ADX_THRESHOLD:
        score = int(score * 0.7)  # کاهش ۳۰٪ امتیاز در روند ضعیف
        reasons.append(f"⚠️ روند ضعیف (ADX={adx:.1f}) → اعتماد کمتر به سیگنال")
    elif adx > 40:
        reasons.append(f"🔥 روند بسیار قوی (ADX={adx:.1f})")
    
    # محدود کردن امتیاز در بازه -۱۰۰ تا +۱۰۰
    score = max(-100, min(100, score))
    
    return score, reasons
