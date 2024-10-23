from django.utils import timezone
import random
import datetime
from django.conf import settings
from feed.middleware import get_current_request
from django.contrib import messages
from .email import send_html_email
import traceback
from .models import MFAToken

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
source_phone = settings.PHONE_NUMBER

def send_text(target_phone, text):
    from twilio.rest import Client
    try:
        client = Client(account_sid, auth_token)
        if len(target_phone) >= 11:
            message = client.messages.create(
                to=target_phone,
                from_=source_phone,
                body=text + ' Text STOP to cancel.')
    except:
        messages.warning(get_current_request(), 'There was an error sending the message.')
        print(traceback.format_exc())

def get_num_length(num, length):
    n = ''
    for x in range(length):
        n = n + str(num)
    return int(n)

def send_verification_text(user, token):
    length = user.profile.verification_code_length
    code = random.randint(get_num_length(1, length), get_num_length(9, length));
    token.token = code
    token.expires = timezone.now() + datetime.timedelta(minutes=settings.AUTH_VALID_MINUTES)
    token.save()
    send_user_text(user, "Your verification code for {} is {}".format(settings.SITE_NAME, str(code)))

def send_verification_email(user, token):
    length = user.profile.verification_code_length
    code = random.randint(get_num_length(1, length), get_num_length(9, length));
    token.token = code
    token.expires = timezone.now() + datetime.timedelta(minutes=settings.AUTH_VALID_MINUTES)
    token.save()
    send_html_email(user, "You have requested a code to access your account. Your verification code for {} is {}".format(settings.SITE_NAME, str(code)), "<p>Dear {},</p><p>Your verification code for {} is {}. Use this code to securely access your account. This email is auto-generated. Please do not reply to this email. If you did not request this code, you can safely disregard this email.</p><h2>{}</h2><p>Sincerely, {}</p>".format(user.profile.name, settings.SITE_NAME, str(code), str(code), settings.SITE_NAME))

def send_user_text(user, text):
    send_text(user.profile.phone_number, text)

def check_verification_code(user, token, code):
    token.attempts = token.attempts + 1
    profile = user.profile
    result = (token != None and code != '' and token.token == code and (token.expires > timezone.now()) and token.attempts <= settings.MFA_TOKEN_ATTEMPTS)
    if token.attempts < 3 and result:
        profile.verification_code_length = 6
    elif token.attempts > 1 and not result:
        profile.verification_code_length = profile.verification_code_length + 2
        if profile.verification_code_length > settings.MFA_TOKEN_LENGTH: profile.verification_code_length = settings.MFA_TOKEN_LENGTH
    token.save()
    profile.save()
    return result
