import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
import django
django.setup()
from lotteh.celery import crypto_trading_bots
crypto_trading_bots()
