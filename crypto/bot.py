from .data import fetch_data
from .signals import get_trade_recommendation
from .models import Bot, Trade
from .binance import create_order, get_crypto_price
from datetime import datetime
import traceback

STOP_LOSS = 0.002
TAKE_PROFIT = 0.002

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
        print(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} TRADING RECOMMENDATION: {trade_rec_type}')
        # STEP 3: EXECUTE THE TRADE
        if (trade_rec_type == 'BUY' and not currently_holding) or (trade_rec_type == 'SELL' and currently_holding):
            last_trade_price = bot.last_trade_price_holding if currently_holding else bot.last_trade_price_not_holding
#            if last_trade_price and (trade_rec_type == 'SELL' and last_trade_price > ticker_data['at'] * (1 - STOP_LOSS) or trade_rec_type == 'BUY' and last_trade_price < ticker_data['at'] * (1 + TAKE_PROFIT)):
#                print('Stop loss/take profit')
#                return
            print(f'Placing {trade_rec_type} order')
            current_price = ticker_data['close'][0]
            amount = round(bot.investment_amount_usd/current_price, 5) if not bot.holding_amount else bot.holding_amount
#            print(amount)
            trade_successful = False
            if not bot.test_mode:
                try:
                    create_order(bot.user, bot.ticker.replace('/','').upper(), trade_rec_type, 'MARKET', amount)
                    trade_successful = True
                except:
                    trade_successful = False
                    print(traceback.format_exc())
            else: trade_successful = True
            currently_holding = (not currently_holding) if trade_successful else currently_holding
            if currently_holding:
                bot.last_trade_price_holding = current_price
            else:
                bot.last_trade_price_not_holding = current_price
            bot.holding_amount = amount
            bot.holding_amount_usd = amount * current_price
            bot.holding = not bot.holding
            bot.save()
            t = Trade.objects.create(ticker=bot.ticker, bot=bot, amount=amount, position=trade_rec_type, amount_usd=amount*current_price)
            bot.notify(trade_rec_type + ' ' + bot.ticker.upper().split('/')[0 if currently_holding else 1] + '/' + bot.ticker.upper().split('/')[1 if currently_holding else 0] - '${}'.format(round(amount * current_price, 2)))
#            if not trade_successful:
 #                print('Failed trade')
  #               return
        else:
            bot.rec = trade_rec_type
            bot.save()
    else:
        print(f'Unable to fetch ticker data - {bot.ticker}. Retrying!!')

