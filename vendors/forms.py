from django import forms
from django.contrib.auth.models import User
from .models import VendorProfile
from femmebabe.settings import CRYPTO_CURRENCIES
from femmebabe.pricing import get_pricing_options
import math

CHOICES = list()
for choice in CRYPTO_CURRENCIES:
    CHOICES.append((choice, choice))

class SendBitcoinForm(forms.Form):
    amount = forms.FloatField()
    bitcoin_address = forms.CharField(min_length=27, max_length=34)

def sub_fee(fee):
    op = ''
    of = len(str(fee))%3
    op = op + str(fee)[0:of] + (',' if of > 0 else '')
    for f in range(math.floor(len(str(fee))/3)):
        op = op + str(fee)[3*f+of:3+3*f+of] + ','
    op = op[:-1]
    return op

def get_pricing():
    choices = []
    for option in get_pricing_options(10):
        choices = choices + [[option, '${} / month'.format(sub_fee(option))]]
    return choices

class VendorProfileUpdateForm(forms.ModelForm):
    PRONOUNS_CHOICES = (
        ('Her', 'She/her/hers'),
        ('Him', 'He/him/his'),
        ('They', 'They/them/theirs'),
        ('Me', 'Just use "me"'),
    )
    pronouns = forms.CharField(widget=forms.Select(choices=PRONOUNS_CHOICES))
    SUBSCRIPTION_CHOICES = (
        ('5', '$5 / month'),
        ('10', '$10 / month'),
        ('15', '$15 / month'),
        ('20', '$20 / month'),
        ('25', '$25 / month'),
        ('50', '$50 / month'),
        ('100', '$100 / month'),
        ('200', '$200 / month'),
        ('500', '$500 / month'),
        ('1000', '$1,000 / month'),
        ('2000', '$2,000 / month'),
    )
    PHOTO_CHOICES = (
        ('5', '$5'),
        ('10', '$10'),
        ('20', '$20'),
        ('25', '$25'),
        ('50', '$50'),
        ('100', '$100'),
    )
    TRIAL_CHOICES = (
        ('0', 'None'),
        ('1', 'One Day'),
        ('2', 'Two Days'),
        ('3', 'Three days'),
        ('7', 'One Week'),
        ('14', 'Two Weeks'),
        ('30', 'One Month'),
        ('60', '60 Days'),
        ('90', '90 Days'),
    )
    subscription_fee = forms.CharField(widget=forms.Select(choices=SUBSCRIPTION_CHOICES))
    payout_currency = forms.CharField(widget=forms.Select(choices=CHOICES))
    photo_tip = forms.CharField(widget=forms.Select(choices=PHOTO_CHOICES))
    free_trial = forms.CharField(widget=forms.Select(choices=TRIAL_CHOICES))
    payout_address = forms.CharField(max_length=300)
    pitch_adjust = forms.IntegerField(required=False)
    def __init__(self, *args, **kwargs):
        super(VendorProfileUpdateForm, self).__init__(*args, **kwargs)
    class Meta:
        model = VendorProfile
        fields = ['activate_surrogacy', 'pronouns', 'address', 'insurance_provider', 'pornhub_link', 'onlyfans_link', 'pitch_adjust', 'subscription_fee', 'free_trial', 'photo_tip', 'payout_currency', 'payout_address']
