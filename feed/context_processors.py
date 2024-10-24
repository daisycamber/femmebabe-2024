from datetime import datetime, time, date, timedelta
from django.conf import settings
from django.contrib.auth.models import User
import pytz, traceback, random, os
from security.models import Session as SecureSession
from feed.models import Post
from security.models import UserIpAddress, UserSession
from security.apis import get_client_ip
from misc.views import current_time
from django.utils import timezone
from security.tests import face_mrz_or_nfc_verified

def utc_to_local(utc_dt, local_tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

from lotteh.celery import async_get_sun
def feed_context(request):
    context_data = dict()
    try:
        context_data['lang'] = request.LANGUAGE_CODE if not request.GET.get('lang', None) else request.GET.get('lang')
    except: context_data['lang'] = settings.DEFAULT_LANG
    context_data['use_prism'] = settings.USE_PRISM
    context_data['use_allauth'] = settings.USE_ALLAUTH
    context_data['icon_url'] = settings.ICON_URL
    context_data['author_name'] = settings.AUTHOR_NAME
    context_data['company_name'] = settings.COMPANY_NAME
    context_data['email_address'] = settings.EMAIL_ADDRESS
    context_data['the_ubi'] = settings.UBI
    context_data['reload_time'] = settings.RELOAD_TIME
    context_data['crypto_provider'] = settings.CRYPTO_PROVIDER
    context_data['default_vibration'] = 400
    context_data['default_crypto'] = settings.DEFAULT_CRYPTO
    context_data['statement_descriptor'] = settings.STATEMENT_DESCRIPTOR
    my_user = User.objects.filter(id=settings.MY_ID).first()
    admin_user = User.objects.filter(id=settings.ADMIN_ID).first()
    context_data['adminusername'] = admin_user.profile.name if admin_user and hasattr(admin_user, 'profile') else None
    context_data['profileusername'] = my_user.profile.name if my_user and hasattr(my_user, 'profile') else 'Daisy'
    context_data['myusername'] = my_user.profile.name if my_user and hasattr(my_user, 'profile') else 'Daisy'
    context_data['my_profile'] = my_user.profile if my_user and hasattr(my_user, 'profile') else None
    context_data['typical_response_time'] = settings.TYPICAL_RESPONSE_TIME_HOURS
    context_data['show_social_links'] = settings.SHOW_SOCIAL_LINKS
    context_data['instagram_link'] = settings.INSTAGRAM_LINK
    context_data['twitter_link'] = settings.TWITTER_LINK
    context_data['youtube_link'] = settings.YOUTUBE_LINK
    context_data['static_url'] = settings.STATIC_SITE_URL
    context_data['admin_email'] = settings.EMAIL_ADDRESS
    context_data['base_description'] = settings.BASE_DESCRIPTION
    context_data['webpush_query_delay'] = settings.WEBPUSH_QUERY_DELAY_SECONDS
    context_data['email_query_delay'] = settings.EMAIL_QUERY_DELAY_SECONDS
    context_data['currentyear'] = datetime.now().year
    context_data['min_age'] = settings.MIN_AGE
    context_data['background_color'] = settings.BACKGROUND_COLOR
    context_data['background_color_dark'] = settings.BACKGROUND_COLOR_DARK
    context_data['agent_name'] = settings.AGENT_NAME
    context_data['agent_phone'] = settings.AGENT_PHONE
    context_data['agent_address'] = settings.ADDRESS
    context_data['the_site_name'] = settings.SITE_NAME
    context_data['domain_name'] = settings.DOMAIN
    if request.path.startswith('/admin/'):
        context_data['full'] = True
    context_data['main_phone'] = settings.PHONE_NUMBER #'+19705857901'
    NoneType = type(None)
    context_data['stacktrace_context'] = traceback.format_exc() if str(traceback.format_exc()) != 'NoneType: None\n' else ''
    context_data['base_url'] = settings.BASE_URL
    user = None
    if hasattr(request, 'user'):
        user = request.user
        context_data['is_admin'] = request.user == admin_user if admin_user else False or request.user.is_superuser
    else:
        context_data['is_admin'] = False
#    day_start = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).replace(hour=0, minute=0, second=0, microsecond=0)
#    day_end = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).replace(hour=23, minute=59, second=59, microsecond=999999)
    if not 'preload' in context_data and not (hasattr(request, 'user') and request.user.is_authenticated):
        context_data['preload'] = True
    context_data['photo_timeout'] = 500
    context_data['show_wishlist'] = settings.SHOW_WISHLIST
    context_data['show_ads'] = settings.SHOW_ADS if (((not hasattr(request, 'user')) or not request.user.is_authenticated) or (request.user.is_authenticated and not request.user.profile.vendor and not User.objects.get(id=settings.MY_ID) in request.user.profile.subscriptions.all())) else False
#    sessions = SecureSession.objects.filter(user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None, ip_address=get_client_ip(request), path=request.path, method=request.method, time__gte=timezone.now() - timedelta(seconds=4))
#    try:
#        context_data['injection_key'] = sessions.last().injection_key
#    except: pass
    if not 'load_timeout' in context_data:
        context_data['load_timeout'] = 600
    context_data['private_text_large'] = settings.PRIVATE_TEXT_LARGE
    context_data['REDIRECT_URL'] = settings.REDIRECT_URL
    if request.GET.get('hidenavbar'): context_data['hidenavbar'] = True
    context_data['webpush'] = {"group": "guests"}
    ip = UserIpAddress.objects.filter(user=None if not hasattr(request, 'user') or not request.user.is_authenticated else request.user, ip_address=get_client_ip(request)).first()
    context_data['current_time'] = str(datetime.now())
    context_data['current_time_text'] = current_time(datetime.now())
    context_data['current_time_digits'] = timezone.now().strftime('%A %B %d, %Y - %H:%M:%S')
    h = int(datetime.now().astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H'))
    context_data['clock_color'] = '#ffcccb' if h >= 9 and h < 21 else 'lightblue'
    if hasattr(request, 'user') and request.user.is_authenticated and ip != None and ip.latitude != None and ip.longitude != None:
        async_get_sun.delay(user.id, request.user.is_authenticated, ip.ip_address)
        sunset = ip.sunset
        sunrise = ip.sunrise
        now = datetime.now(pytz.timezone(ip.timezone)) if ip.timezone else timezone.now()
        if now < sunrise or now > sunset:
            context_data['darkmode'] = True
        context_data['current_time'] = str(now)
        context_data['current_time_text'] = current_time(now)
        context_data['current_time_digits'] = now.strftime('%A %B %d, %Y - %H:%M:%S')
        h = int(now.strftime('%H'))
        context_data['clock_color'] = '#ffcccb' if h >= 9 and h < 21 else 'lightblue'
    sess = None
#    if hasattr(request, 'user') and request.user and request.user.is_authenticated: sess = UserSession.objects.filter(user=request.user if hasattr(request, 'user') else None, session_key=request.session.session_key).order_by('-timestamp').first()
#    sm = (sess and not sess.authorized if sess else True) and (not request.path.startswith('/verify/age/') and not request.path.startswith('/accounts/tfa/') and not request.path.startswith('/security/mrz/') and not request.path.startswith('/security/nfc/') and not request.path.startswith('/webauth/verify/')) and (hasattr(request, 'user') and request.user.is_authenticated and request.user.profile.vendor)
    context_data['securitymodal'] = request.security_modal if hasattr(request, 'security_modal') and request.security_modal else None
    context_data['securitymodaljs'] = request.security_modal if hasattr(request, 'security_modal') and request.security_modal else None
#    context_data['securitymodaljs'] = sm
    context_data['payment_processor'] = 'square'
    context_data['hiderrm'] = True
    context_data['polling_now'] = timezone.now() < datetime(2024, 11, 6).replace(tzinfo=pytz.timezone(settings.TIME_ZONE))
    return context_data
