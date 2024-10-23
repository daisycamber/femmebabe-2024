from django.contrib.auth.models import User
from users.tfa import send_user_text
import requests
from shell.execute import run_command
from django.conf import settings
import json
import time

KEYS = 'api_key={}&api_token={}'.format(settings.TENSORDOCK_KEY, settings.TENSORDOCK_TOKEN)
SERVER = 'server={}'.format(settings.TENSORDOCK_SERVER)

BASE_ENDPOINT_URL = 'https://marketplace.tensordock.com/api/v0/'
BILLING_ENDPOINT_URL = BASE_ENDPOINT_URL + 'billing?{}'.format(KEYS)
STOP_ENDPOINT_URL = BASE_ENDPOINT_URL + 'stop/single?{}&{}'.format(KEYS, SERVER)
TIMEOUT=30
REVIEW_TIMEOUT=60 * 15 # A quarter hour

def get_balance():
    response = requests.get(BILLING_ENDPOINT_URL, timeout=TIMEOUT)
    j = response.json()
    return float(j['balance'])

def stop_server():
    r = requests.get(STOP_ENDPOINT_URL, timeout=TIMEOUT)
    print(str(r.json()))

def review_server():
    balance = get_balance()
    if balance < settings.SERVER_SHUTDOWN_THRESHOLD:
        print('Powering off server to save money with ${} remaining balance.'.format(settings.SERVER_SHUTDOWN_THRESHOLD))
        send_user_text(User.objects.get(id=settings.MY_ID), '{} has been powered off to save money. Please add to your balance and restart to continue using the server.'.format(settings.SITE_NAME))
        run_command('sudo systemctl stop celeryd')
        run_command('sudo systemctl stop celeryd_beat')
        run_command('sudo systemctl stop apache2')
        run_command('sudo poweroff')
        time.sleep(REVIEW_TIMEOUT)
        stop_server()
    else: print('Server has ${} in funds available, keeping her alive.'.format(balance))
