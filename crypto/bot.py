from .data import fetch_data
from .signals import get_trade_recommendation
from .models import Bot, Trade
from .binance import create_order, get_crypto_price
from datetime import datetime

STOP_LOSS = 0.000000001
TAKE_PROFIT = 0.000000002

def run_bot_once(id):
    bot = Bot.objects.get(id=id)
    currently_holding = bot.holding
    # STEP 1: FETCH THE DATA
    ticker_data = None
    try:
        ticker_data = fetch_data(bot.ticker)
    except: pass
    if ticker_data is not None:
        # STEP 2: COMPUTE THE TECHNICAL INDICATORS & APPLY THE TRADING STRATEGY
        trade_rec_type = get_trade_recommendation(ticker_data)
        print(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}  TRADING RECOMMENDATION: {trade_rec_type}')
        # STEP 3: EXECUTE THE TRADE
        if (trade_rec_type == 'BUY' and not currently_holding) or (trade_rec_type == 'SELL' and currently_holding):
            last_trade_price = bot.last_trade_price_holding if currently_holding else bot.last_trade_price_not_holding
#            if last_trade_price and (trade_rec_type == 'SELL' and last_trade_price > ticker_data['at'] * (1 - STOP_LOSS) or trade_rec_type == 'BUY' and last_trade_price < ticker_data['at'] * (1 + TAKE_PROFIT)):
#                print('Stop loss/take profit')
#                return
            print(f'Placing {trade_rec_type} order')
            current_price = ticker_data['at']
            amount = round(bot.investment_amount_usd/current_price, 5) if not bot.holding_amount else bot.holding_amount
            trade_successful = True if bot.test_mode else create_order(bot.user, bot.ticker.replace('/','').upper(), trade_rec_type, 'MARKET', amount)
            if not trade_successful: return
            currently_holding = not currently_holding if trade_successful else currently_holding
            if currently_holding:
                bot.last_trade_price_holding = current_price
            else:
                bot.last_trade_price_not_holding = current_price
            bot.holding_amount = amount
            bot.holding_amount_usd = amount * current_price
            bot.holding = currently_holding
            bot.save()
            t = Trade.objects.create(ticker=bot.ticker, bot=bot, amount=amount, position=trade_rec_type, amount_usd=amount*current_price)
    else:
        print(f'Unable to fetch ticker data - {bot.ticker}. Retrying!!')
