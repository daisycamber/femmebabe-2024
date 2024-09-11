from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN

timeouts = {}

RATE_LIMIT = 5

@csrf_exempt
def sms(request):
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.auth.decorators import user_passes_test
    from vendors.tests import is_vendor
    from feed.tests import identity_verified
    from django.http import HttpResponse
    from django.contrib.auth.models import User
    import threading, time
    from django.conf import settings
    from feed.templatetags.nts import number_to_string
    from chat.models import Message
    from users.tfa import send_user_text
    from users.logout import logout_user, logout_all
    from datetime import timedelta
    from twilio.twiml.voice_response import VoiceResponse, Gather
    from twilio.twiml.messaging_response import MessagingResponse
    global RATE_LIMIT
    global timeouts
    from twilio.rest import Client
    from_phone = User.objects.get(id=settings.MY_ID).profile.phone_number #'+14255358727'
    phone = request.POST.get('From', '')
    resp = MessagingResponse()
    if timeouts[phone] and timezone.now() - timeouts[phone] > timedelta(seconds=1):
        return HttpResponse(str(resp), content_type='text/xml')
    timeouts[phone] = timezone.now()
    message = request.POST.get('Body', None)
    m = ''
    if message:
        m = message.lower()
    user = None
    users = User.objects.filter(profile__phone_number=phone).order_by('-profile__last_seen')
    if users.count() > 0:
        user = users.first()
    if not user:
        resp.message('You need an account to message and call me. This site is age restricted, so do not message or call if you are under {} ({}). Join {} at {}/accounts/register/ ({}+)'.format(number_to_string(settings.MIN_AGE), settings.MIN_AGE, settings.SITE_NAME.capitalize(), settings.BASE_URL, settings.MIN_AGE))
    elif m == 'stop':
        for u in users:
            u.profile.phone_number = '+1'
            u.save()
        resp.message('You are now unsubscribed.')
    elif m == 'logout':
        if user.is_superuser:
            logout_all()
            resp.message('You have logged all users out, {}'.format(User.objects.get(id=settings.MY_ID).profile.name))
        else:
            logout_user(user)
            resp.message('You have been logged out, {}'.format(User.objects.get(id=settings.MY_ID).profile.name))
    elif m == 'how are you':
        resp.message(User.objects.get(id=settings.MY_ID).profile.status)
    elif m == 'details':
        resp.message(settings.DOMAIN.capitalize() + " is a beauty and health blog. Visit today at {}".format(settings.BASE_URL))
    elif m == 'login':
        resp.message("Log in to {} here - {}".format(settings.DOMAIN.capitalize(), settings.BASE_URL + user.profile.create_face_url()))
    elif m == 'photo':
        extra = ''
        me = User.objects.get(id=settings.MY_ID)
        msg = resp.message("Here is the latest photo of me." + extra)
        if not (me in user.profile.subscriptions.all()):
            msg.media(settings.BASE_URL + User.objects.get(id=settings.MY_ID).profile.get_face_blur_url())
        else:
            msg.media(settings.BASE_URL + User.objects.get(id=settings.MY_ID).profile.get_public_image_url())
    else:
        resp.message("Hi {}, thanks for reaching out! You can send me things like 'how are you', 'details', 'login' and 'photo' (for a photo of me), or message me in the chat.".format(user.profile.name))
        msg = Message.objects.create(sender=user,recipient=User.objects.get(id=settings.MY_ID), content=message)
        msg.save()
        send_user_text(User.objects.get(id=settings.MY_ID), '@{} says: {}'.format(user.profile.name, message))
    return HttpResponse(str(resp), content_type='text/xml')
