from django.utils import timezone
from django.contrib.auth.models import User
from .models import SessionDedup
from django.utils.deprecation import MiddlewareMixin
import traceback
import uuid, re
import datetime
from feed.middleware import set_current_exception
from django.contrib.sessions.models import Session as SecureSession
from security.apis import get_client_ip, check_ip_risk
from stacktrace.models import Error
from uuid import UUID
from django.conf import settings

RISK_LEVEL = 1
FRAUD_MOD = settings.PAGE_LOADS_PER_API_CALL

def get_uuid():
    filename = "%s" % (uuid.uuid4())
    return filename

def get_qs(get_data):
    get_length = 0
    qs = '?'
    if get_data:
        for key, value in get_data.items():
            qs = qs + '{}={}&'.format(key, value)
            get_length = get_length + 1
    try:
        if qs[-1] == '&':
            qs = qs[:-1]
        if qs[-1] == '?':
            qs = qs[:-1]
        if qs[-1] == '&':
            qs = qs[:-1]
    except: pass
    return qs

redirect_paths = ['verify', 'accounts', 'face', 'admin', 'kick', 'appeal', 'auth', 'recovery', 'barcode', 'time', 'feed/secure', 'logs', 'feed/grid/api', 'feed/profile', 'shell/edit', 'serviceworker.js', 'security', 'melanin', 'terms', 'feed/secure', 'hypnosis', 'payments/idscan', 'payments/webdev', 'sitemap.xml', 'news.xml', 'webauth', 'remote']

def redirect_path(path):
#    if path == '/': return False
    for p in redirect_paths:
       pa = '/{}'.format(p)
       if path.startswith(pa):
           return False
    return True

def redirect_request(request):
    if request.method == 'POST':
        return False
    return True

def uuid_valid(id):
    UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
    if UUID_PATTERN.match(id):
        return True
    return False

def unique_list(l):
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist

from lotteh.celery import async_process_user_request

# birthing middleware
def security_middleware(get_response):
    def middleware(request):
        response = None
        try:
            ip = get_client_ip(request)
            qs = get_qs(request.GET)
            sd = SessionDedup.objects.create(user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None, ip_address=ip, path=request.path, querystring=qs, method=request.method)
            sd.async_delete()
            sessions = SessionDedup.objects.filter(user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None, ip_address=ip, path=request.path, querystring=qs, method=request.method, time__gte=timezone.now() - datetime.timedelta(seconds=10))
            if request.method == 'POST':
                from django.http import HttpResponseRedirect
                if sessions.count() < settings.SESSION_INDEX and request.method == 'POST': return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                if sessions.count() > settings.SESSION_INDEX and request.method == 'POST': return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#            print('{} - {}'.format(ip, request.path + ((qs) if qs else '') + '*' + str(sessions.count())))
            from security.models import UserIpAddress
            ip_obj = request.user.security_profile.ip_addresses.filter(ip_address=ip).first() if request.user.is_authenticated else UserIpAddress.objects.filter(ip_address=ip, user=None).first()
            if ip_obj and ip_obj.risk_detected and not request.path == '/kick/reasess/':
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect(settings.REDIRECT_URL)
            request.GET._mutable = True
            if request.user.is_authenticated and request.user.profile.vendor and redirect_path(request.path):
                from security.models import UserSession
                sess = UserSession.objects.filter(user=request.user, session_key=request.session.session_key).order_by('-timestamp').first()
                if not sess:
                    sess, created = UserSession.objects.get_or_create(user=request.user, session_key=request.session.session_key, user_agent=request.META["HTTP_USER_AGENT"], authorized=False)
                if not sess.authorized:
                    request.security_modal = True
                    from security.build import get_next_redirect
                    red = get_next_redirect(request)
                    if red: return red
            async_process_user_request.delay(ip, request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None, True if hasattr(request, 'user') and request.user.is_authenticated else False, request.path, request.META.get('CONTENT_LENGTH'), request.META.get('HTTP_REFERER'), qs, request.method, sessions.count())
        except:
            try:
                Error.objects.create(user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None, stack_trace=traceback.format_exc(), notes='Logged by security middleware.')
            except: pass
            set_current_exception(traceback.format_exc())
            print(traceback.format_exc())
        response = get_response(request)
        return response
    return middleware
