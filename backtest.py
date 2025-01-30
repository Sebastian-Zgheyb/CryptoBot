import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yaml

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
    
config = load_config()
# Parameters
CRYPTO = config['crypto']
PRICE_THRESHOLD = config["price_threshold"]
INITIAL_BALANCE = 10000
ATR_MULTIPLIER_SL = config["atr_multiplier_sl"]
ATR_MULTIPLIER_TP = config["atr_multiplier_tp"]
lot_size = 0.1

# Connect to MT5
if not mt5.initialize():
    print("MT5 initialize failed with error code =", mt5.last_error())
    quit()

def fetch_mt5_data(symbol, timeframe, days=30):
    rates = mt5.copy_rates_range(symbol, timeframe, datetime.today() - timedelta(days=days), datetime.now())
    return pd.DataFrame(rates) if rates is not None else None

def calculate_atr(data, period=14):
    df = data.copy()
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift(1))
    df['tr3'] = abs(df['low'] - df['close'].shift(1))
    df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['true_range'].rolling(window=period).mean()
    return df['atr']

def backtest(symbol=CRYPTO, timeframe=mt5.TIMEFRAME_M10):
    data = fetch_mt5_data(symbol, timeframe)
    if data is None:
        print("Failed to fetch data from MT5.")
        return
    
    data['atr'] = calculate_atr(data)
    
    balance = INITIAL_BALANCE
    max_balance = balance
    equity_curve = [INITIAL_BALANCE]
    drawdowns = []
    wins, losses = 0, 0
    total_profit, total_loss = 0, 0
    trade_results = []
    
    for i in range(14, len(data) - 1):  # Start after ATR period
        price = data['close'][i]
        atr = data['atr'][i]

        if np.isnan(atr):
            continue

        # Define SL and TP
        sl = price - ATR_MULTIPLIER_SL * atr
        tp = price + ATR_MULTIPLIER_TP * atr
        
        # Calculate price percentage difference
        difference = abs((price - data['close'][i - 1]) / data['close'][i - 1] * 100)
        
        # First check
        if difference > PRICE_THRESHOLD:
            # Second check on the next bar (simulating live "8 sec re-check")
            next_difference = (data['close'][i + 1] - price) / price * 100
            if next_difference > PRICE_THRESHOLD:
                trade_fee = lot_size * price * (0.01)
                # Simulate TP/SL hit on the next candle
                if data['high'][i + 1] >= tp:  # TP hit
                    balance += lot_size * (tp - price) - trade_fee
                    wins += 1
                    total_profit += (tp - price) - trade_fee
                    trade_results.append((tp - price) / (price - sl))
                elif data['low'][i + 1] <= sl:  # SL hit
                    balance -= lot_size * (price - sl) + trade_fee
                    losses += 1
                    total_loss += (price - sl) + trade_fee
                    trade_results.append(-1)
                
                
            equity_curve.append(balance)
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

    # Curves
    # Equity curve
    plt.figure(figsize=(12, 6))
    plt.plot(range(len(equity_curve)), equity_curve, label="Equity Curve", color='blue', linewidth=2)
    max_drawdown_index = np.argmin(equity_curve)  # Index of the lowest equity point
    plt.scatter(max_drawdown_index, equity_curve[max_drawdown_index], color='red', label="Max Drawdown", zorder=3)
    plt.title("Equity Curve", fontsize=14, fontweight='bold')
    plt.xlabel("Trades", fontsize=12)
    plt.ylabel("Balance ($)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()

    # Drawdown Over Time curve
    drawdown_series = [max_balance - b for b in equity_curve]
    plt.figure(figsize=(10, 5))
    plt.plot(drawdown_series, color='red', label="Drawdown")
    plt.fill_between(range(len(drawdown_series)), drawdown_series, alpha=0.3, color='red')
    plt.title("Drawdown Over Time")
    plt.xlabel("Trades")
    plt.ylabel("Drawdown ($)")
    plt.legend()
    plt.show()

    # Trade Distribution curve
    plt.figure(figsize=(8, 5))
    plt.hist(trade_results, bins=20, color='blue', alpha=0.7, edgecolor='black')
    plt.title("Distribution of Trade Outcomes")
    plt.xlabel("R-Multiple (Reward/Risk)")
    plt.ylabel("Frequency")
    plt.show()

    # Win/Loss Streaks curve
    plt.figure(figsize=(12, 6))
    plt.plot(data['close'], label="Price", color='black', alpha=0.6)
    print(trade_results)
    for i in range(len(trade_results)):
        if trade_results[i] > 0:  # Winning trade
            plt.scatter(i, data['close'][i], color='green', label="Win" if i == 0 else "")
        else:  # Losing trade
            plt.scatter(i, data['close'][i], color='red', label="Loss" if i == 0 else "")

    plt.title("Trade Entries & Exits on Price Chart")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()

    # Cumulative Profit/Loss curve
    cumulative_pnl = np.cumsum(trade_results)
    plt.figure(figsize=(10, 5))
    plt.plot(cumulative_pnl, label="Cumulative Profit/Loss", color="purple")
    plt.axhline(0, linestyle="--", color="black", alpha=0.5)
    plt.title("Cumulative Profit/Loss Over Time")
    plt.xlabel("Trades")
    plt.ylabel("Profit/Loss (R-Multiple)")
    plt.legend()

    plt.show()

if __name__ == '__main__':
    backtest()
    mt5.shutdown()
