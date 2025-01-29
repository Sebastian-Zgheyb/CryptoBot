from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from itertools import count
import time
import MetaTrader5 as mt5
import yaml

load_dotenv()

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
    
config = load_config()

# Assign config values
CRYPTO = config["crypto"]
PRICE_THRESHOLD = config["price_threshold"]
STOP_LOSS = config["stop_loss"]
TAKE_PROFIT = config["take_profit"]
EQUITY_DIVIDER = config["equity_divider"]
ORDER_TYPE = mt5.ORDER_TYPE_BUY if config["order_type"] == "BUY" else mt5.ORDER_TYPE_SELL
server = config["server"]

# Global variables
last_logged_ticket = None
initial_sell_logged = False

# Load account credentials from environment variables
account_number = int(os.getenv(config["account_number_env"]))
password = os.getenv(config["password_env"])

# Connect to the MT5 trade account
if not mt5.initialize():
    print("MT5 initialize failed with error code =", mt5.last_error())
    quit()

authorized = mt5.login(account_number, password, server)

if authorized:
    print(f'Connected to account #{account_number}')
else:
    print(f'Failed to connect to account #{account_number}, error code: {mt5.last_error()}')

# Store account equity
account_info = mt5.account_info()
if account_info is None:
    raise RuntimeError('Could not load the account equity level.')
else:
    equity = float(account_info[10])

def get_dates():
    """Use dates to define the range of our dataset in the `get_data() function"""
    utc_from = datetime.today() - timedelta(days=1)
    return utc_from, datetime.now()

def get_data():
    """Download one day of 10 minute candles, along with the buy and sell prices for bitcoin."""
    utc_from, utc_to = get_dates()
    return mt5.copy_rates_range('BTCUSD!', mt5.TIMEFRAME_M10, utc_from, utc_to)

def get_current_price():
    """Return current buy price."""
    current_buy_price = mt5.symbol_info_tick("BTCUSD!")[2]
    return current_buy_price

def log_closed_positions():
    """Log information about closed positions."""
    global last_logged_ticket, initial_sell_logged

    from_date, to_date = get_dates()

    deals = mt5.history_deals_get(from_date, to_date)
    if deals is None:
        print(f"Error retrieving deal history: {mt5.last_error()}")
        return
    
    # Filter for sell deals related to the bot
    sell_deals = [deal for deal in deals if deal.symbol == CRYPTO and deal.magic == 100 and deal.type == mt5.ORDER_TYPE_SELL]

    if not sell_deals:
        return
    
    most_recent_deal = max(sell_deals, key=lambda deal: deal.time)
    
    if not initial_sell_logged:
        last_logged_ticket = most_recent_deal.ticket
        initial_sell_logged = True  # Skip the first detected sell as initial state
        return
    
    # Log information about the most recent sell
    if most_recent_deal.ticket != last_logged_ticket:
        last_logged_ticket = most_recent_deal.ticket
        print(f"SELL ORDER placed: Ticket={most_recent_deal.ticket}, Symbol={most_recent_deal.symbol}, "
            f"Type={most_recent_deal.type}, Volume={most_recent_deal.volume}, Price={most_recent_deal.price}, "
            f"Profit={most_recent_deal.profit:.10f}, Time={datetime.fromtimestamp(most_recent_deal.time)}\n")
        
def trade():
    """Determine if we should trade and if so, send requests to MT5."""
    candles = get_data()
    current_buy_price = get_current_price()

    symbol_info = mt5.symbol_info(CRYPTO)
    raw_lot = (equity / EQUITY_DIVIDER) / current_buy_price
    lot = max(symbol_info.volume_min, round(raw_lot / symbol_info.volume_step) * symbol_info.volume_step)

    difference = (candles['close'][-1] - candles['close'][-2]) / candles['close'][-2] * 100

    positions = mt5.positions_get(symbol=CRYPTO)
    orders = mt5.orders_get(symbol=CRYPTO)

    if difference > PRICE_THRESHOLD:
        time.sleep(8) # Pause for re-check
        candles = get_data()
        difference = (candles['close'][-1] - candles['close'][-2]) / candles['close'][-2] * 100

        if difference > PRICE_THRESHOLD and not positions and not orders:
            price = mt5.symbol_info_tick(CRYPTO).bid

            sl = price - (price * STOP_LOSS) / 100 if ORDER_TYPE == mt5.ORDER_TYPE_BUY else price + (price * STOP_LOSS) / 100
            tp = price + (price * TAKE_PROFIT) / 100 if ORDER_TYPE == mt5.ORDER_TYPE_BUY else price - (price * TAKE_PROFIT) / 100

            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': CRYPTO,
                'volume': lot,
                'type': ORDER_TYPE,
                'price': price,
                'sl': sl,
                'tp': tp,
                'magic': 100,
                'comment': 'python-buy',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }

            # Send a trading request
            result = mt5.order_send(request)

            # Check the execution result
            print(f'Trying to buy {CRYPTO} {lot} lots at {price}')

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f'BUY ORDER failed, return code={result.retcode}')
            else:
                print(f"BUY ORDER placed: {result}\n")

if __name__ == '__main__':
    print('Press Ctrl-C to stop.')
    try:
        for i in count():
            trade()
            log_closed_positions()
    except KeyboardInterrupt:
        print("Shutting down...")
        mt5.shutdown()
