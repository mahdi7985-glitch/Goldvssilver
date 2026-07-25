from config.settings import (
    STOP_LOSS_ATR_MULTIPLIER, TAKE_PROFIT_ATR_MULTIPLIER,
    MAX_CAPITAL_RISK, TRADING_FEE, MIN_PROFIT_AFTER_FEE
)

def calculate_risk(price, atr, capital=100000000, metal_type='silver'):
    """
    محاسبه حد ضرر و سود پویا با فاصله منطقی
    price: قیمت به تومان
    atr: نوسان به تومان
    """
    if price <= 0 or atr <= 0:
        return {
            'stop_loss': 0,
            'take_profit': 0,
            'gross_profit': 0,
            'net_profit': 0,
            'quantity': 0,
            'quantity_display': 'ندارد (ورود توصیه نمی‌شود)',
            'is_profitable': False,
            'suggestion': '⚠️ ورود توصیه نمی‌شود',
            'explanation': 'قیمت یا نوسان معتبر نیست.',
            'metal_name': 'نقره' if metal_type == 'silver' else 'طلا',
            'max_capital_risk': 0
        }
    
    # محاسبه ATR با حداقل ۱٪ قیمت برای جلوگیری از فاصله کم
    min_atr = price * 0.01
    effective_atr = max(atr, min_atr)
    
    # حد ضرر و سود با فاصله منطقی
    stop_loss = price - (STOP_LOSS_ATR_MULTIPLIER * effective_atr)
    take_profit = price + (TAKE_PROFIT_ATR_MULTIPLIER * effective_atr)
    
    # اطمینان از حداقل فاصله ۳٪ برای حد ضرر و ۵٪ برای حد سود
    min_stop_distance = price * 0.03
    min_profit_distance = price * 0.05
    
    if (price - stop_loss) < min_stop_distance:
        stop_loss = price - min_stop_distance
    if (take_profit - price) < min_profit_distance:
        take_profit = price + min_profit_distance
    
    # سود ناخالص و خالص
    gross_profit = ((take_profit / price) - 1) * 100
    net_profit = gross_profit - (TRADING_FEE * 100)
    
    # حجم معامله
    max_risk_amount = capital * MAX_CAPITAL_RISK
    quantity = max_risk_amount // price if price > 0 else 0
    
    # پیشنهاد معامله
    is_profitable = net_profit >= (MIN_PROFIT_AFTER_FEE * 100)
    
    if quantity == 0:
        suggestion = '⚠️ ورود توصیه نمی‌شود'
        explanation = 'حجم معامله بسیار کم است. برای ورود نیاز به سرمایه بیشتری دارید.'
        quantity_display = 'ندارد (ورود توصیه نمی‌شود)'
    elif not is_profitable:
        suggestion = '❌ معامله نکن'
        explanation = f'سود خالص ({net_profit:.1f}%) کمتر از حداقل ({MIN_PROFIT_AFTER_FEE*100:.0f}%) است.'
        quantity_display = f"{int(quantity):,} گرم"
    elif net_profit > 10:
        suggestion = '🔥 معامله کن (فرصت عالی)'
        explanation = f'سود خالص {net_profit:.1f}% بسیار خوب است.'
        quantity_display = f"{int(quantity):,} گرم"
    elif net_profit > 5:
        suggestion = '📈 معامله کن'
        explanation = f'سود خالص {net_profit:.1f}% مناسب است.'
        quantity_display = f"{int(quantity):,} گرم"
    else:
        suggestion = '⚖️ صبر کن'
        explanation = f'سود خالص {net_profit:.1f}% کم است. بهتر است صبر کنید.'
        quantity_display = f"{int(quantity):,} گرم"
    
    return {
        'stop_loss': round(stop_loss, 0),
        'take_profit': round(take_profit, 0),
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'quantity': int(quantity),
        'quantity_display': quantity_display,
        'is_profitable': is_profitable,
        'suggestion': suggestion,
        'explanation': explanation,
        'metal_name': 'نقره' if metal_type == 'silver' else 'طلا',
        'max_capital_risk': MAX_CAPITAL_RISK * 100
    }
