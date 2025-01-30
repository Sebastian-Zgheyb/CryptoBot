# 📌 CryptoBot: Automated Trading with MetaTrader 5

This is an automated trading bot developed using Python and the **MetaTrader 5 API** to execute cryptocurrency trades based on real-time market analysis. It utilizes **stop loss and take profit orders, ATR-based position sizing, and backtesting** to optimize trading efficiency and allow users to test their strategies.

---

## 🚀 **Setup Guide: Getting Started with CryptoBot**

### **1️⃣ Install MetaTrader 5 (MT5)**
To use this bot, you need **MetaTrader 5**, which allows Python integration for algorithmic trading.

- **Download MT5:** [MetaTrader 5 Official Website](https://www.metatrader5.com/en/download)
- Install it on your system and launch the platform.

---

### **2️⃣ Create a Free Demo Account**
You need an account to access live or historical market data.

1. Open **MetaTrader 5**.
2. Go to **File** → **Open an Account**.
3. Choose a broker (or use the default MetaQuotes demo server).
4. Fill in the required details and create your demo account.
5. Once set up, go to **Tools** → **Options** → **Expert Advisors** and check **"Allow WebRequest for listed URLs"**.

---

### **3️⃣ Install Dependencies**
This bot requires Python and some external libraries. Install them with:

```sh
pip install MetaTrader5 pandas numpy matplotlib
```

---

### **4️⃣ Configure Your MT5 Connection**
In the **Python script**, update the login credentials with your **account number and password**.

```python
import MetaTrader5 as mt5

# Connect to MetaTrader 5
mt5.initialize()

# Login to your account
account = 12345678  # Replace with your demo/live account number
password = "your_password"
server = "Your_Broker_Server"

if not mt5.login(account, password, server):
    print("Login failed")
else:
    print("Connected successfully!")
```

---

### **5️⃣ Run the Backtest**
To test the bot before live trading, run:

```sh
python backtest.py
```

This will simulate trades on historical data, calculating performance metrics such as **profit factor, win/loss ratio, drawdown, and equity curves**.

---

### **6️⃣ Live Trading (Use with Caution ⚠️)**
Once you're comfortable with backtesting, you can deploy the bot for live trading.

Run:

```sh
python cryptobot.py
```

🚨 **Warning**: Test with a **demo account** first before using real funds. Trading involves risks.

---

## 📊 **Features & Functionality**
✅ **ATR-based Stop Loss & Take Profit** – Adapts to market volatility.  
✅ **Backtesting Engine** – Run historical tests to validate strategies.  
✅ **Performance Metrics** – Tracks equity, drawdown, win/loss ratio, and more.  
✅ **Auto-Reconnect** – Handles MT5 connection drops.  

---

## 💡 **Troubleshooting**
- If MT5 **fails to connect**, check:
  - The correct **server name** (found in your MT5 terminal).
  - If your account has **trading permissions** enabled.
  - If your **MT5 terminal is running** in the background.

- If **no trades are being executed**, verify:
  - The strategy conditions in `cryptobot.py`.
  - That you have **enough balance** in your demo/live account.

---

## 🔗 **Resources & Useful Links**
- 📘 **MetaTrader 5 Python API Docs**: [https://www.mql5.com/en/docs/python_metatrader5](https://www.mql5.com/en/docs/python_metatrader5)  
- 📈 **Trading Strategy Basics**: [https://www.investopedia.com/trading-strategies-4580205](https://www.investopedia.com/trading-strategies-4580205)  
