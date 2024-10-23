import os
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth.models import User
from .views import interactive

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


def call(phone):
    status = User.objects.get(id=settings.MY_ID).profile.status
    call = client.calls.create(
#        twiml='<Response><Say>{}</Say></Response>'.format(status),
        url=interactive('scheduled for mel'),
        to=phone,
        from_=settings.PHONE_NUMBER
    )
