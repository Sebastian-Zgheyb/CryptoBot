import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Parameters
INITIAL_BALANCE = 10000
ATR_MULTIPLIER_SL = 1.5
ATR_MULTIPLIER_TP = 2.5
lot_size = 0.1

# Connect to MT5
if not mt5.initialize():
    print("MT5 initialize failed with error code =", mt5.last_error())
    quit()

def fetch_mt5_data(symbol, timeframe, days=30):
    utc_from = datetime.today() - timedelta(days=days)
    rates = mt5.copy_rates_range(symbol, timeframe, utc_from, datetime.now())
    return pd.DataFrame(rates) if rates is not None else None

def calculate_atr(data, period=14):
    df = data.copy()
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['true_range'].rolling(window=period).mean()
    return df['atr']

def backtest(symbol='BTCUSD!', timeframe=mt5.TIMEFRAME_M10):
    data = fetch_mt5_data(symbol, timeframe)
    if data is None:
        print("Failed to fetch data from MT5.")
        return
    
    data['atr'] = calculate_atr(data)
    balance = INITIAL_BALANCE
    max_balance = balance
    drawdowns = []
    wins, losses = 0, 0
    total_profit, total_loss = 0, 0
    trade_results = []

    for i in range(14, len(data) - 1):  # Start after ATR period
        price = data['close'][i]
        atr = data['atr'][i]
        if np.isnan(atr):
            continue
        
        sl = price - ATR_MULTIPLIER_SL * atr
        tp = price + ATR_MULTIPLIER_TP * atr
        
        if price > data['close'][i - 1]:  # Simple momentum entry
            if data['high'][i + 1] >= tp:  # TP hit
                balance += lot_size * (tp - price)
                wins += 1
                total_profit += (tp - price)
                trade_results.append((tp - price) / (price - sl))
            elif data['low'][i + 1] <= sl:  # SL hit
                balance -= lot_size * (price - sl)
                losses += 1
                total_loss += (price - sl)
                trade_results.append(-1)
        
        drawdowns.append((max_balance - balance) / max_balance if balance < max_balance else 0)
        max_balance = max(max_balance, balance)
    
    max_drawdown = max(drawdowns) * 100  # Convert to percentage
    profit_factor = (total_profit / abs(total_loss)) if total_loss != 0 else np.inf
    win_loss_ratio = wins / losses if losses != 0 else np.inf
    avg_r_multiple = np.mean(trade_results) if trade_results else 0
    
    print(f"Final Balance: {balance:.2f}")
    print(f"Win/Loss Ratio: {win_loss_ratio:.2f}")
    print(f"Profit Factor: {profit_factor:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Average R-Multiple: {avg_r_multiple:.2f}")

if __name__ == '__main__':
    backtest()
    mt5.shutdown()