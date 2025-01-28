Log number: 1
Date and time: 22nd January, 1:03pm

What the bot is currently capable of:
- Can connect to MetaTrader 5 (MT5)
    1. Authenticates and connects to a trading account using account credentials and environment variables

- Retrieve account and market data
    1. Fetches account equity and uses it to calculate position sizes
    2. Retrieves current buy and sell prices of BTCUSD

- Analyse price movements
    1. Calculates percentage difference between last two 10-minute candles to identify potential trading signals

- Trade execution
    1. Can place buy or sell orders based on price thresholds
    2. Automatically calculates position size based on account equity
    3. Sets stop loss (SL) and take profit (TP) levels as percentages of the order price.

- Error handling for market conditions
    1. Checks for existing positions and orders before placing a new trade

- Basic automation
    1. Repeatedly evaluates trading conditions and executes trades in a loop

Everything up until this point has been guided through: https://www.cryptomaton.org/2021/03/14/how-to-code-your-own-crypto-trading-bot-python/

I will now set goals for this project and work on them independently.

Coding goals include:
1. Refactoring my code
    - Splitting my code into separate files for easier maintenance
    - Using a main.py file to manage the bot's flow
    - Improving variable naming

2. Configurability
    - Creating a config file for configurable parameters to avoid hardcoding in script:
        - Trading pairs (BTCUSD)
        - Price thresholds, stop loss, and take profit percentages

3. Error Handling and Fail-Safes
    - Adding better exception handling to ensure bot doesn't crash unexpectedly by wrapping key sections in try-except blocks (e.g. handle errors when fetching data from MT5 or when trades fail)
    - Implement a kill switch (add a manual override mechanism to stop all trading if something goes wrong - through key press or remote flag)

4. Replace print() statements with Python's logging module for different kinds of events

5. (Optional) Allow the user to smoothly switch between a test mode and real mode if they want to test strategies on a demo account rather than their main account

6. Input validation
    - Validate parameters like STOP_LOSS and TAKE_PROFIT to ensure they are within reasonable ranges (1-20)
    - Periodically confirm MT5 is connected and the trading account is active

7. Basic Performance Metrics
    - Track and Print Performance:
        - Keep a running tally of:
            - Total trades executed.
            - Total profit/loss (realized and unrealized).
            - Win/loss ratio.
        - Display a summary every n iterations.

Functionality goals include: 
1. Improve logging and monitoring
    - Add detailed logs:
        - Log all actions (e.g. trades placed, price changes, errors) to a file for later analysis
        - Include timestamps, trade details, and errors in the logs
    - Real-Time Notifications
        - Send alerts via email for executed trades or critical errors

2. Implement backtesting
    - Historical Testing:
        - Add functionality to backtest the trading strategy on historical data.
        - Simulate trades using past price data to evaluate the strategy's profitability

    - Metrics Calculation:
        - Measure performance metrics like profit/loss, drawdowns, and Sharpe ratio during backtesting

3. Risk Management Enhancements
    - Dynamic Position Sizing: 
        - Adjust position sizes based on volatility or account equity to minimise risk
    
    - Trailing Stop Loss:
        - Replace the fixed stop loss with a trailing stop loss to lock in profits as the price moves favourably

4. Add more trading strategies
    - Additional indicators:
        - Incorporate indicators like RSI, MACD, or moving averages for more refined trading signals
    
    - Time-Based strategies:
        - Limit trading to specific time windows when volatility is higher (e.g. during market opening)

5. Portfolio Diversification
    - Multi-currency support:
        - Extend the bot to trade multiple cryptocurrencies (e.g. ETHUSD, LTCUSD) and manage a diversified portfolio
    
    - Asset allocation:
        - Allocate a percentage of equity to each asset dynamically based on predefined rules

6. Add Investing Features
    - DCA (Dollar-Cost Averaging)
        - Automatically buy small amounts of cryptocurrency at regular intervals regardless of price

    - Rebalancing 
        - Periodically rebalance your portfolio to maintain target allocations.

7. Data Visualisation
    - Performance Dashboard:
        - Build a simple web dashboard or terminal-based UI to display:
            - Account balance, equity, and current portfolio
            - Historial trade data and performance metrics
            - Real-time price charts and trade signals

8. Deploy to the cloud
    - Continuous Operation
        - Deploy my bot to a cloud provider like AWS, Azure, or Google Cloud for 24/7 trading
    
    - Reliability improvements
        - Add mechanisms to restart the bot in case of failures or crashes
    
9. Advanced Strategies
    - Sentiment Analysis:
        - Integrate social media sentiment analysis (e.g. from X or Reddit) to gauge market sentiment
            - (Useful in cases when looking for certain keywords like TRUMP or ELON to navigate pump and dumps)

    - Machine Learning Models:
        - Use ML algorithms to predict price movement based on historical patterns.


Log number: 2
Date and time: 28th January, 5:55pm

I figured it could be confusing for some users to understand how the bot sells. 
When an order is made, the bot automatically sends the corresponding take profit and stop loss limits we set in our code.
When the price of the cryptocurrency we are trading soars up to the take profit percentage, or plummets to the stop loss percentages, the bot SELLS.
Originally, there was no logging for this event. Now, there is. 

Additionally, users must make sure to enable algorithmic trading on MT5 or the bot won't trade.
This is done by going to MT5 -> Tools -> Options -> Expert Advisors -> Check algorithmic trading.
I also fixed an issue where the bot would try to execute the trade with a volume below the minimum volume of that cryptocurrency.
The original creator of this bot recommended increasing the amount of equity we allocate, but I decided to make the bot choose between 
the amount of equity we try to allocate or the minimum volume required for that coin. For testing purposes, this will suffice,
but for a user using real money, I will ensure it relies on the user's equity solely to prevent it always performing trades
even when the equity is below what the user would like to be trading, i.e. the user can't afford such trades or didn't intend to make them.

Volume means the amount of that currency we are trying to trade, so if there is a 0.01 BTC volume minimum, it means we have to at least
trade 0.01 BTC at a time.

Log number: 3
Date and time: 28th Jan, 6pm

I do not see the reason for the bot to constantly spam info about the coin or the difference in the last two closing prices.
I believe it would be more meaningful for the bot to only print details about BUY orders and SELL orders (when it hits SL or TP).
Thus, I will modify the bot to only log BUYs and SELLs and not general info every tick. 

Log number: 4
Date and time: 28th Jan, 7pm

Sweet, the bot now only logs the BUY and SELL orders.
I've noticed the bot ALWAYS loses money on it's trades. I believe this is due to the fact that, for these testing purposes, 
it sells after such miniscule increases and decreases in price that the gas/transaction fees always overwhelm whatever profit
our take profit even would have made.

E.g. If you buy $100 worth of bitcoin, then sell at $101, the transaction fees most trading platforms use will easily
be greater than that $1 of profit.

Realistically too for non crypto traders, when you buy that $100 of bitcoin, it would appear as $98-99 in your account
after the transaction fees take place, so yeah those fees are pesky. 

While this is an issue that should be resolved with having more substantial take profit and stop loss percentages,
it could be worth trying to track the gas fees/spread. 

Taking a look now, there are no fees when it comes to using MT5 through XBTFX!

You just have to deal with the spread, which is the difference between the BUY and SELL prices of the coin.

For example, if the Bid price is $103,000 and the Ask price is $103,100, the spread is $100. 
This means that, as soon as you place a trade, you start with a loss of $100 (because you bought at $103,100, 
but if you were to immediately sell, you’d get $103,000). The spread is your "cost of entry" into the trade.

This means that with a spread of, say, 0.5%, whenever I buy, I'm already down 0.5% from when I sell, meaning
I'd need the price to go up by 0.5% to even BREAK EVEN. I'm selling at like 0.002% or something now LOL.

That's why it never makes profit. Now that I know my bot can sell and buy properly, I'm going to experiment using
actual figures.