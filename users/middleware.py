from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib import messages
from users.models import Profile
from django.shortcuts import redirect
from django.urls import reverse
import urllib, json
from threading import local
import urllib.request
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, HttpResponseRedirect
import uuid
from django.contrib.auth import logout
from feed.middleware import set_current_exception, get_current_exception
from voice.models import VoiceProfile
from django.contrib.sessions.models import Session as SecureSession
from stacktrace.models import Error
from security.apis import get_client_ip
from security.middleware import get_qs
from django.conf import settings
from feed.models import Post
from security.models import UserIpAddress
from django.contrib.auth.models import User
import datetime

_user = local()

class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _user.value = request.user


def get_current_user():
    try:
        return _user.value if _user.value.is_authenticated else None
    except AttributeError:
        return None

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_timezone(ip):
    url = 'http://ip-api.com/json/' + ip
    req = urllib.request.Request(url)
    out = urllib.request.urlopen(req).read()
    o = json.loads(out)
    return o['timezone']

redirect_paths = ['accounts/login', 'accounts/tfa', 'verify', 'face', 'barcode', 'survey', 'payments']

def redirect_path(path):
#    if path == '/': return False
    for p in redirect_paths:
       if path.startswith('/{}'.format(p)):
           return False
    return True

from lotteh.celery import async_user_tasks

def simple_middleware(get_response):
    # One-time configuration and initialization.
    def middleware(request):
        response = None
        try:
            if request.user.is_authenticated and not request.user.is_active: logout(request)
            if not request.session.session_key:
                request.session.save()
            next = request.GET.get('next', False)
            if (next == '/accounts/logout/'):
                request.GET._mutable = True
                request.GET.pop('next')
                qs = ''
                for key, value in request.GET.items():
                    qs = qs + '{}={}&'.format(key, value)
                return HttpResponseRedirect(request.path + '?' + qs)
            ip = get_client_ip(request)
            async_user_tasks.delay(request.user.is_authenticated, request.user.id if request.user.is_authenticated else None, ip, request.LANGUAGE_CODE)
            if request.user.is_authenticated and (request.user.profile.enable_two_factor_authentication or request.user.profile.vendor) and not request.path.startswith('/accounts/tfa/') and not request.path.startswith('/accounts/logout/') and not request.path.startswith("/face/") and not request.path.startswith("/verify/"):
                if not request.user.profile.phone_number or len(request.user.profile.phone_number) < 11:
                    return HttpResponseRedirect(reverse('users:tfa_onboarding'))
            response = get_response(request)
            if request.COOKIES.get('user_signup', False):
                request.user_signup = True
            if request.path != '/verify/age/' and request.COOKIES.get('push_cookie'):
                request.has_push_cookie = True
            if request.path != '/verify/age/' and not request.COOKIES.get('push_cookie'):
                max_age = settings.PUSH_COOKIE_EXPIRATION_HOURS * 60 * 60
                expires = datetime.datetime.strftime(
                    datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                    "%a, %d-%b-%Y %H:%M:%S GMT",
                )
                response.set_cookie('push_cookie', True, max_age=max_age, expires=expires)
        except:
            try:
                Error.objects.create(user=request.user if request.user.is_authenticated else None, stack_trace=get_current_exception(), notes='Logged by users middleware.')
            except: pass
            set_current_exception(traceback.format_exc())
            print(traceback.format_exc())
        response = get_response(request)
        return response
    return middleware
