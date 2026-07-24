from config.settings import (
    STOP_LOSS_ATR_MULTIPLIER, TAKE_PROFIT_ATR_MULTIPLIER,
    MAX_CAPITAL_RISK, TRADING_FEE, MIN_PROFIT_AFTER_FEE
)

def calculate_risk(price, atr, capital=100000000, metal_type='silver'):
    """
    محاسبه حد ضرر، سود و پیشنهاد معامله برای طلا یا نقره
    """
    # حد ضرر و سود پویا
    stop_loss = price - (STOP_LOSS_ATR_MULTIPLIER * atr)
    take_profit = price + (TAKE_PROFIT_ATR_MULTIPLIER * atr)
    
    # سود ناخالص و خالص
    gross_profit = ((take_profit / price) - 1) * 100
    net_profit = gross_profit - (TRADING_FEE * 100)
    
    # حجم معامله
    max_risk_amount = capital * MAX_CAPITAL_RISK
    quantity = max_risk_amount // price
    
    # پیشنهاد معامله
    is_profitable = net_profit >= (MIN_PROFIT_AFTER_FEE * 100)
    
    if is_profitable:
        if net_profit > 10:
            suggestion = "🔥 پیشنهاد خرید قوی"
        elif net_profit > 5:
            suggestion = "📈 پیشنهاد خرید"
        else:
            suggestion = "⚖️ پیشنهاد نگهداری"
    else:
        suggestion = "❌ پیشنهاد معامله نکن"
    
    # نوع فلز
    metal_name = "نقره" if metal_type == 'silver' else "طلا"
    
    return {
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'quantity': int(quantity),
        'is_profitable': is_profitable,
        'suggestion': suggestion,
        'metal_name': metal_name,
        'max_capital_risk': MAX_CAPITAL_RISK * 100
    }
