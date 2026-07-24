from config.settings import (
    STOP_LOSS_ATR_MULTIPLIER, TAKE_PROFIT_ATR_MULTIPLIER,
    MAX_CAPITAL_RISK, TRADING_FEE, MIN_PROFIT_AFTER_FEE
)

def calculate_risk(price, atr, capital=100000000):
    """محاسبه حد ضرر و سود پویا"""
    stop_loss = price - (STOP_LOSS_ATR_MULTIPLIER * atr)
    take_profit = price + (TAKE_PROFIT_ATR_MULTIPLIER * atr)
    
    # محاسبه سود خالص بعد از کارمزد
    profit_percent = ((take_profit / price) - 1) * 100
    net_profit = profit_percent - (TRADING_FEE * 100)
    
    # حجم معامله پیشنهادی
    max_risk_amount = capital * MAX_CAPITAL_RISK
    quantity = max_risk_amount // price
    
    # آیا معامله به صرفه است؟
    is_profitable = net_profit >= (MIN_PROFIT_AFTER_FEE * 100)
    
    return {
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'net_profit': net_profit,
        'quantity': int(quantity),
        'is_profitable': is_profitable,
        'max_capital_risk': MAX_CAPITAL_RISK * 100
    }
