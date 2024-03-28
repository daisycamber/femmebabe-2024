import urllib.parse
import hashlib
import hmac
import base64
import requests
import time

api_url = "https://api.binance.us"

# get binanceus signature
def get_binanceus_signature(data, secret):
    postdata = urllib.parse.urlencode(data)
    message = postdata.encode()
    byte_key = bytes(secret, 'UTF-8')
    mac = hmac.new(byte_key, message, hashlib.sha256).hexdigest()
    return mac

# Attaches auth headers and returns results of a POST request
def binanceus_request(uri_path, data, api_key, api_sec):
    headers = {}
    headers['X-MBX-APIKEY'] = api_key
    signature = get_binanceus_signature(data, api_sec)
    payload={
        **data,
        "signature": signature,
        }
    req = requests.post((api_url + uri_path), headers=headers, data=payload)
    return req.text

from django.conf import settings

def create_order(user, symbol,side,type,quantity):
    api_key = user.crypto_trading_profile.binance_api_key
    secret_key = user.crypto_trading_profile.binance_api_secret
    uri_path = "/api/v3/order"
    data = {
        "symbol": symbol,
        "side": side,
        "type": type,
        "quantity": quantity,
        "timestamp": int(round(time.time() * 1000))
    }
    result = binanceus_request(uri_path, data, api_key, secret_key)
    if result['status'] == 'FILLED': return True
    return False

def get_crypto_price(ticker):
    resp = requests.get('https://api.binance.us/api/v3/ticker/price?symbol={}'.format(ticker))
    return float(resp.json()['price'])
