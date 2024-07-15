import talib
import numpy as np

FAST_PERIOD = 7
SLOW_PERIOD = 14
SIGNAL_PERIOD = 5
RSI_PERIOD = 3
RSI_OVERBOUGHT = 65
RSI_OVERSOLD = 35

def get_trade_recommendation(ticker_df):
    macd_result, final_result = 'WAIT','WAIT'
    # BUY or SELL based on MACD crossover points and the RSI value at that point
    macd, signal, hist = talib.MACD(ticker_df['close'], fastperiod = FAST_PERIOD, slowperiod = SLOW_PERIOD, signalperiod = SIGNAL_PERIOD)
    last_hist = hist.iloc[-1]
    prev_hist = hist.iloc[-2]
    if not np.isnan(prev_hist) and not np.isnan(last_hist):
        # If hist value has changed from negative to positive or vice versa, it indicates a crossover
        macd_crossover = (abs(last_hist + prev_hist)) != (abs(last_hist) + abs(prev_hist))
        if macd_crossover:
            macd_result = 'BUY' if last_hist > 0 else 'SELL'
    if macd_result != 'WAIT':
        print('macd !wait')
        rsi = talib.RSI(ticker_df['close'], timeperiod = RSI_PERIOD)
        last_rsi = rsi.iloc[-1]
        print(last_rsi)
        if (last_rsi <= RSI_OVERSOLD):
            final_result = 'BUY'
        elif (last_rsi >= RSI_OVERBOUGHT):
            final_result = 'SELL'
    return final_result
