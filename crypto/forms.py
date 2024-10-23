from django import forms
import datetime
from django.conf import settings
from .models import CryptoTradingProfile, Bot

TRADING_CRYPTO = settings.CRYPTO_CURRENCIES

CHOICES = list()
for choice in TRADING_CRYPTO:
    CHOICES.append((choice, choice))

class NewBotForm(forms.Form):
    primary_ticker = forms.ChoiceField(
        required=True, choices=CHOICES, widget=forms.RadioSelect()
    )
    secondary_ticker = forms.ChoiceField(
        required=True, choices=CHOICES, widget=forms.RadioSelect()
    )

class EditCryptoTradingProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditCryptoTradingProfileForm, self).__init__(*args, **kwargs)
    class Meta:
        model = CryptoTradingProfile
        fields = ('binance_api_key','binance_api_secret',)

class EditBotForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditBotForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Bot
        fields = ('investment_amount_usd','test_mode','live',)
