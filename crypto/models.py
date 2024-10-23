from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class CryptoTradingProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='crypto_trading_profile')
    binance_api_key = models.TextField(default='')
    binance_api_secret = models.TextField(default='')

def notify_user(user, message):
    from django.conf import settings
    payload = {"head": '[Crypto] {}'.format(message), "url": settings.BASE_URL + '/crypto/', 'icon': '{}{}'.format(settings.BASE_URL, settings.ICON_URL)}
    from pwa_webpush import send_user_notification
    send_user_notification(user=user, payload=payload, ttl=1000)

class Bot(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_bots')
    ticker = models.CharField(max_length=20, default='')
    rec = models.CharField(max_length=20, default='')
    holding = models.BooleanField(default=False)
    investment_amount_usd = models.FloatField(default=0)
    holding_amount_usd = models.FloatField(default=0)
    holding_amount = models.FloatField(default=0)
    last_trade_price_not_holding = models.FloatField(default=0)
    last_trade_price_holding = models.FloatField(default=0)
    test_mode = models.BooleanField(default=False)
    live = models.BooleanField(default=True)

    def notify(self, message):
        notify_user(self.user, message)


class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name='trades')
    ticker = models.CharField(max_length=20, default='')
    position = models.CharField(max_length=10, default='')
    amount = models.FloatField(default=0)
    amount_usd = models.FloatField(default=0)
    timestamp = models.DateTimeField(default=timezone.now)
