import json
import requests

def get_crypto_price(crypto):
    key = "https://api.binance.us/api/v3/ticker/price?symbol="
    currencies = ["{}USD".format(crypto)]
    j = 0
    for i in currencies:
        url = key+currencies[j]
        data = requests.get(url)
        data = data.json()
        j = j+1
        return float(data['price'])
