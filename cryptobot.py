from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from itertools import count
import time
import MetaTrader5 as mt5

load_dotenv()

CRYPTO = 'BTCUSD!'
last_logged_ticket = None
initial_sell_logged = False
# REAL VALUES
# Price threshold (percentage)
# PRICE_THRESHOLD = 3
# # Stop loss (percentage)
# STOP_LOSS = 5
# # Take profit (percentage)
# TAKE_PROFIT = 8

# TESTING VALUES
# Price threshold (percentage)
PRICE_THRESHOLD = 0.001
# Stop loss (percentage)
STOP_LOSS = 0.00166666666
# Take profit (percentage)
TAKE_PROFIT = 0.0016999999

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

# This function is used to get the dates for our dataset - so one day's worth of data in our case as we only care about the last two 10 minute candles
def get_dates():
    """Use dates to define the range of our dataset in the `get_data() function"""
    utc_from = datetime.today() - timedelta(days=1)
    return utc_from, datetime.now()

def get_data():
    """Download one day of 10 minute candles, along with the buy and sell prices for bitcoin."""
    utc_from, utc_to = get_dates()
    return mt5.copy_rates_range('BTCUSD!', mt5.TIMEFRAME_M10, utc_from, utc_to)

def get_current_prices():
    """Return current buy and sell prices."""
    # print(mt5.symbol_info_tick("BTCUSD!"))
    current_buy_price = mt5.symbol_info_tick("BTCUSD!")[2]
    # current_sell_price = mt5.symbol_info_tick("BTCUSD!")[1]
    return current_buy_price

# this logs when the bot sells so we can see when the bot closes a position
def log_closed_positions():
    """Log information about closed positions."""
    global last_logged_ticket, initial_sell_logged

    from_date = datetime.now() - timedelta(days=1)
    to_date = datetime.now()

    # get history of deals in the past day
    deals = mt5.history_deals_get(from_date, to_date)
    if deals is None:
        print(f"Error retrieving deal history: {mt5.last_error()}")
        return
    
    relevant_deals = [
        deal for deal in deals if deal.symbol == CRYPTO and deal.magic == 100
    ]

    if not relevant_deals:
        print("No recent deals to log")
        return
    
    # find the most recent deal
    most_recent_deal = max(relevant_deals, key=lambda deal: deal.time)
    
    if not initial_sell_logged and most_recent_deal.type == 1:  # "1" for sell orders
        # Skip this deal since it is likely the initial state
        last_logged_ticket = most_recent_deal.ticket
        initial_sell_logged = True  # Mark that the first "sell" has been skipped
        return
    
    # Log information about the most recent deal
    if most_recent_deal.ticket != last_logged_ticket:
        last_logged_ticket = most_recent_deal.ticket
        print("SELL ORDER!!!")
        print(f"Most recent deal closed: Ticket={most_recent_deal.ticket}, Symbol={most_recent_deal.symbol}, "
            f"Type={most_recent_deal.type}, Volume={most_recent_deal.volume}, Price={most_recent_deal.price}, "
            f"Profit={most_recent_deal.profit:.10f}, Time={datetime.fromtimestamp(most_recent_deal.time)}\n")
        

    
def trade():
    """Determine if we should trade and if so, send requests to MT5."""
    utc_from, utc_to = get_dates()
    candles = get_data()
    current_buy_price = get_current_prices()

    symbol_info = mt5.symbol_info(CRYPTO)
    raw_lot = (equity / 20) / current_buy_price  # Risk management formula
    lot = max(symbol_info.volume_min, round(raw_lot / symbol_info.volume_step) * symbol_info.volume_step)
    # print(lot)

    # keep the sleep for debugging because otherwise it iterates too fast
    # time.sleep(2)

    # now, we calculate the percent difference between the current price and the close price of the previous candle
    difference = (candles['close'][-1] - candles['close'][-2]) / candles['close'][-2] * 100

    # check if the position has already been placed
    positions = mt5.positions_get(symbol=CRYPTO)
    orders = mt5.orders_get(symbol=CRYPTO)
    symbol_info = mt5.symbol_info(CRYPTO)
    # print(difference, PRICE_THRESHOLD)
    # now, we perform our logic checks
    if difference > PRICE_THRESHOLD:
        # print(f'dif 1: {CRYPTO}, {difference}')
        # Pause for 8 seconds to make sure the increase is sustained
        time.sleep(8)

        # Update utc_from and utc_to to reflect the new time range
        utc_from, utc_to = get_dates()  # Call get_dates() again to refresh the timestamps

        # calculate the difference once again 
        candles = mt5.copy_rates_range(CRYPTO, mt5.TIMEFRAME_M10, utc_from, utc_to)
        difference = (candles['close'][-1] - candles['close'][-2]) / candles['close'][-2] * 100

        if difference > PRICE_THRESHOLD:
            # print(f'dif 2: {CRYPTO}, {difference}')
            price = mt5.symbol_info_tick(CRYPTO).bid
            # print(f'{CRYPTO} is up {str(difference)}% in the last 5 minutes, trying to open BUY position.')

            # prepare the trade request
            if not mt5.initialize():
                raise RuntimeError(f'MT5 initialize() failed with error code {mt5.last_error()}')
            
            # check that there are no open positions or orders
            if len(positions) == 0 and len(orders) < 1:
                if symbol_info is None:
                    print(f'{CRYPTO} not found, can not call order_check()')
                    mt5.shutdown()
                    
                # if the symbol is not available in MarketWatch, add it
                if not symbol_info.visible:
                    print(f'{CRYPTO} is not visible, trying to switch on')
                    if not mt5.symbol_select(CRYPTO, True):
                        print('symbol_select() failed, exit', CRYPTO)
                        
                
                # this represents 5% equity. the minimum order is 0.01 BTC. Increase equity share if retcode = 10014
                # lot = float(round(((equity / 20) / current_buy_price), 2))
                # print(lot)

                if ORDER_TYPE == BUY:
                    sl = price - (price * STOP_LOSS) / 100
                    tp = price + (price * TAKE_PROFIT) / 100
                else:
                    sl = price + (price * STOP_LOSS) / 100
                    tp = price - (price * TAKE_PROFIT) / 100

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

                # send a trading request
                result = mt5.order_send(request)

                # check the execution result
                # print(f'1. order_send(): by {CRYPTO} {lot} lots at {price}')

                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f'2. order_send() failed, retcode={result.retcode}')
                print(f"BUY ORDER!!!")
                # print the order result - anything else than retcode=10009 is an error in the trading request
                print(f'Buy order complete: {result}\n')

                # print(f'opened position with POSITION_TICKET={result.order}')

            else:
                pass
                # print(f'BUY signal detected, but {CRYPTO} has {len(positions)} active trade')
        else:
            pass

    else:
        if orders or positions:
            # print('BUY signal detected but there is an already an active trade')
            pass
        else: 
            # uncomment this if you feel lonely with how the terminal print anything when the difference is too low
            print(f'Difference is only: {round((difference), 2)}%. Trying again...')
            pass

if __name__ == '__main__':
    print('Press Ctrl-C to stop.')
    try:
        for i in count():
            # print(f'Iteration {i + 1}')
            trade()
            log_closed_positions()
    except KeyboardInterrupt:
        print("Shutting down...")
        mt5.shutdown()
