from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.conf import settings
from security.views import all_unexpired_sessions_for_user

def send_expiry_notifications():
    for user in User.objects.filter(is_active=True, profile__admin=True):
        for session in all_unexpired_sessions_for_user(user):
            if session.expire_date < timezone.now() + datetime.timedelta(minutes=60) and session.expire_date > timezone.now():
                payload = {
                    'head': 'Your session is about to expire on {}'.format(settings.SITE_NAME),
                    'body': 'This session will expire in {} minutes with {}'.format((session.expire_date - timezone.now()).minutes, settings.SITE_NAME),
                    'icon': settings.BASE_URL + settings.ICON_URL,
                    'url': settings.BASE_URL,
                }
                from pwa_webpush import send_user_notification
                try:
                    send_user_notification(user, payload=payload)
                except: pass