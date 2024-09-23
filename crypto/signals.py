import talib
import numpy as np

alt = False
digits = 0

def fix(digit):
    return round(digit * 1.0/24 * 6, 2)

FAST_PERIOD = 12 if not alt else fix(12)
SLOW_PERIOD = 26 if not alt else fix(26)
SIGNAL_PERIOD = 9 if not alt else fix(9)
RSI_PERIOD = 3 if not alt else fix(9)
RSI_OVERBOUGHT = 45
RSI_OVERSOLD = 55

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
#    print('{} - {}'.format(macd_result, final_result))
    return final_result
