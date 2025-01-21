
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from itertools import count
import time
import MetaTrader5 as mt5

load_dotenv()

CRYPTO = 'BTCUSD'

# Price threshold (percentage)
PRICE_THRESHOLD = 3
# Stop loss (percentage)
STOP_LOSS = 5
# Take profit (percentage)
TAKE_PROFIT = 8

# Replace in line 113 to choose between a BUY or SELL order
BUY = mt5.ORDER_TYPE_BUY
SELL = mt5.ORDER_TYPE_SELL
ORDER_TYPE = BUY

# connect to the trade account without specifying a password and a server
if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

# account number in the top left corner of the MT5 terminal window
# the terminal database password is applied if connection data is set to be remembered
account_number = 2121944313
password = os.getenv("MT5_PASSWORD")  # Get password from environment variable
authorized = mt5.login(account_number, password=password, server="XBTFX-MetaTrader5")

if authorized:
    print(f'connected to account #{account_number}')
else:
    print(f'failed to connect at account #{account_number}, error code: {mt5.last_error()}')

# store the equity of your account
account_info = mt5.account_info()
if account_info is None:
    raise RuntimeError('Could not load the account equity level.')
else:
    equity = float(account_info[10])

print(equity)


# This function is used to get the dates for our dataset - so one day's worth of data in our case as we only care about the last two 10 minute candles
def get_dates():
    """Use dates to define the range of our dataset in the `get_data() function"""
    utc_from = datetime.today() - timedelta(days=1)
    return utc_from, datetime.now()

def get_data():
    """Download one day of 10 minute candles, along with the buy and sell prices for bitcoin."""
    utc_from, utc_to = get_dates()
    return mt5.copy_rates_range('BTCUSD', mt5.TIMEFRAME_M10, utc_from, utc_to)

def get_current_prices():
    """Return current buy and sell prices."""
    current_buy_price = mt5.symbol_info_tick("BTCUSD")[2]
    current_sell_price = mt5.symbol_info_tick("BTCUSD")[1]
    return current_buy_price, current_sell_price

print(mt5.shutdown())
