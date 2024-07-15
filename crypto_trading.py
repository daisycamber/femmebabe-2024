import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
import django
django.setup()
from femmebabe.celery import crypto_trading_bots
crypto_trading_bots()
