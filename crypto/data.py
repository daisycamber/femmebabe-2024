import ccxt
import pandas as pd

CANDLE_DURATION_IN_MIN = 5
exchange = ccxt.binanceus()

# STEP 1: FETCH THE DATA
def fetch_data(ticker):
    global exchange
    bars,ticker_df = None, None
    bars = exchange.fetch_ohlcv(ticker, timeframe=f'{CANDLE_DURATION_IN_MIN}m', limit=100)
    if bars is not None:
        ticker_df = pd.DataFrame(bars[:-1], columns=['at', 'open', 'high', 'low', 'close', 'vol'])
        ticker_df['Date'] = pd.to_datetime(ticker_df['at'], unit='ms')
        ticker_df['symbol'] = ticker
    return ticker_df