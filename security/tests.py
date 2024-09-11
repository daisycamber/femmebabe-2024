from django.test import TestCase
from django.utils import timezone
import datetime
from django.conf import settings

def request_passes_test(test_func, login_url=None, redirect_field_name='next'):
    """
    Decorator for views that checks that the request passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the request object and returns True if the request passes.
    """

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            # urlparse chokes on lazy objects in Python 3, force to str
            resolved_login_url = force_str(
                resolve_url(login_url or settings.LOGIN_URL))
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator

def pin_verified(request):
    user = request.user
    return user.security_profile.pincode == '' or ((user.pincodes.filter(valid=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.PIN_REQUIRED_MINUTES)).count() > 0 and user.pincodes.filter(valid=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.PIN_REQUIRED_MINUTES)).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.PIN_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def biometric_verified(request):
    user = request.user
    return not user.profile.enable_biometrics or user.webauth_devices.count() == 0 or ((user.biometric.filter(valid=True, session_key=request.session.session_key).count() > 0 and user.biometric.filter(valid=True, session_key=request.session.session_key).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.BIOMETRIC_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def recent_face_match(request):
    user = request.user
    return user.is_authenticated and (user.faces.filter(session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.RECENT_FACE_MATCH_REQUIRED_MINUTES)).first() or user.user_sessions.filter(bypass=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def mrz_verified(request):
    user = request.user
    return user.is_authenticated and ((user.mrz_scans.filter(valid=True, session_key=request.session.session_key).count() > 0 and user.mrz_scans.filter(valid=True, session_key=request.session.session_key).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.MRZ_SCAN_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def nfc_verified(request):
    user = request.user
    return user.is_authenticated and ((user.nfc_scans.filter(valid=True, session_key=request.session.session_key).count() > 0 and user.nfc_scans.filter(valid=True, session_key=request.session.session_key).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.NFC_SCAN_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=request.session.session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def mrz_or_nfc_verified(request):
    user = request.user
    return user.is_authenticated and mrz_verified(request) or nfc_verified(request)

def face_mrz_or_nfc_verified(request):
    user = request.user
    return user.is_authenticated and (recent_face_match(request) or mrz_or_nfc_verified(request))

def recent_face_match_skey(user, session_key):
    return user.is_authenticated and (user.faces.filter(session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.RECENT_FACE_MATCH_REQUIRED_MINUTES)).first() or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def mrz_verified_skey(user, session_key):
    return user.is_authenticated and ((user.mrz_scans.filter(valid=True, session_key=session_key).count() > 0 and user.mrz_scans.filter(valid=True, session_key=session_key).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.MRZ_SCAN_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def nfc_verified_skey(user, session_key):
    return user.is_authenticated and ((user.nfc_scans.filter(valid=True, session_key=session_key).count() > 0 and user.nfc_scans.filter(valid=True, session_key=session_key).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.NFC_SCAN_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def mrz_or_nfc_verified_skey(user, session_key):
    return user.is_authenticated and (mrz_verified_skey(user, session_key) or nfc_verified_skey(user, session_key)) or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0

def pin_verified_skey(user, session_key):
    return user.security_profile.pincode == '' or ((user.pincodes.filter(valid=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.PIN_REQUIRED_MINUTES)).count() > 0 and user.pincodes.filter(valid=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.PIN_REQUIRED_MINUTES)).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.PIN_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def biometric_verified_skey(user, session_key):
    return user.profile.enable_biometrics or user.webauth_devices.count() == 0 or ((user.biometric.filter(valid=True, session_key=session_key).count() > 0 and user.biometric.filter(valid=True, session_key=session_key).last().timestamp > timezone.now() - datetime.timedelta(minutes=settings.BIOMETRIC_REQUIRED_MINUTES)) or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)

def face_mrz_or_nfc_verified_session_key(user, session_key):
    print(user.is_authenticated)
    print(pin_verified_skey(user, session_key))
    print(recent_face_match_skey(user, session_key))
    print(mrz_or_nfc_verified_skey(user, session_key))
    return user.is_authenticated and ((pin_verified_skey(user, session_key) and (recent_face_match_skey(user, session_key) or mrz_or_nfc_verified_skey(user, session_key))) or user.user_sessions.filter(bypass=True, session_key=session_key, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).count() > 0)
