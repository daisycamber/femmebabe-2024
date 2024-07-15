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


def simple_middleware(get_response):
    # One-time configuration and initialization.
    def middleware(request):
        response = None
        try:
            if not request.user.is_active: logout(request)
            if not request.session.session_key:
                request.session.save()
#                request.session.session_key # (Session)
            next = request.GET.get('next', False)
            if (next == '/accounts/logout/'):
                request.GET._mutable = True
                request.GET.pop('next')
                qs = ''
                for key, value in request.GET.items():
                    qs = qs + '{}={}&'.format(key, value)
                return HttpResponseRedirect(request.path + '?' + qs)
            ip = get_client_ip(request)
            redirect_url = reverse(settings.LOGIN_REDIRECT_URL) + settings.LOGIN_REDIRECT_QUERYSTRING #, kwargs={'username': User.objects.filter(id=settings.MY_ID).first().profile.name})
            if request.method == 'GET' and request.path == '/' and not request.GET.get('k') and not request.META.get('HTTP_REFERRER'):
# and UserIpAddress.objects.filter(ip_address=ip, timestamp__gte=timezone.now()-datetime.timedelta(hours=24*settings.SESSION_FILTER_DAYS)).first() 
                if request.user.is_authenticated and request.user.profile.vendor:
                    return HttpResponseRedirect(reverse('go:go'))
#                else:
#                    extra = ''
#                    addr = UserIpAddress.objects.filter(ip_address=ip, timestamp__gte=timezone.now()-datetime.timedelta(hours=24*settings.SESSION_FILTER_DAYS)).first()
#                    if addr and addr.user and addr.user.profile.vendor:
#                        extra = '?next=/go/' if not next else '?next=' + next
#                        return HttpResponseRedirect(reverse('users:login') + extra)
                elif not request.COOKIES.get('return_visit'):
                    max_age = settings.LANDING_COOKIE_EXPIRATION_DAYS * 24 * 60 * 60
                    expires = datetime.datetime.strftime(
                        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                        "%a, %d-%b-%Y %H:%M:%S GMT",
                    )
                    response = HttpResponseRedirect(reverse('landing:index'))
                    response.set_cookie('return_visit', True, max_age=max_age, expires=expires)
                    return response
#                        return HttpResponseRedirect(redirect_url + '&k=' + request.GET.get('k', str(uuid.uuid4())))
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                user = get_object_or_404(User, pk=request.user.pk)
                # Update last visit time after request finished processing.
                request.user.profile.last_seen = timezone.now()
                try:
                    request.user.profile.language_code = request.LANGUAGE_CODE
                except: request.user.profile.language_code = settings.DEFAULT_LANG
                last_ip = request.user.profile.ip
                request.user.profile.ip = get_client_ip(request)
                try:
                    request.user.profile.save()
                except:
                    print(traceback.format_exc())
                if request.user.profile.identity_verified:
                    if not hasattr(request.user, 'voice_profile'):
                        voice_profile = VoiceProfile.objects.create(user=request.user)
                        voice_profile.save()
            elif not hasattr(request.user, 'profile') and isinstance(request.user, User):
                p = Profile()
                p.email_verified = True
                p.user = request.user
                p.save()
#                return HttpResponseRedirect(reverse('feed:home'))
#            if request.user.is_authenticated and request.user.profile.enable_two_factor_authentication and request.user.profile.tfa_expires < timezone.now():
#                messages.warning(request, 'Your session has expired. Please log in again to continue using the site')
#                s = SecureSession.objects.all()
#                logout(request)
            if request.user.is_authenticated and (request.user.profile.enable_two_factor_authentication or request.user.profile.vendor) and not request.path.startswith('/accounts/tfa/') and not request.path.startswith('/accounts/logout/') and not request.path.startswith("/face/") and not request.path.startswith("/verify/"):
                if not user.profile.phone_number or len(user.profile.phone_number) < 11:
                    return HttpResponseRedirect(reverse('users:tfa_onboarding'))
#            if request.path.startswith('/accounts/logout/') and request.GET.get('message', None) and request.GET.get('k', None):
#                messages.warning(request, request.GET.get('message'))
#                return HttpResponseRedirect(reverse('users:logout'))
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
