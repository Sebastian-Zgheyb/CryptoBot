
from datetime import datetime
from itertools import count
import time

import MetaTrader5 as mt5

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
mt5.initialize()

# account number in the top left corner of the MT5 terminal window
# the terminal database password is applied if connection data is set to be remembered
account_number = 17225
authorized = mt5.login(account_number)

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