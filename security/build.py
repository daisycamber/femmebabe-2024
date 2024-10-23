def async_build_session(user_id, session_key):
    from .models import UserSession
    if not get_auth(user_id, session_key):
        us = UserSession.objects.filter(user__id=user_id, session_key=session_key)
        for u in us:
            u.authorized = False
            u.save()

def async_build_sessions():
    from .models import UserSession
    from django.conf import settings
    from django.utils import timezone
    import datetime
    for s in UserSession.objects.filter(user__profile__vendor=True, timestamp__gte=timezone.now() - datetime.timedelta(hours=24*30)).order_by('-timestamp'):
        async_build_session(s.user.id, s.session_key)

def sync_patch_session(user_id, session_key):
    from .models import UserSession
    us = UserSession.objects.filter(user__id=user_id, session_key=session_key)
    for u in us:
        u.authorized = True
        u.save()

def get_auth(user_id, session_key):
    from security.tests import face_mrz_or_nfc_verified_session_key, pin_verified_skey, biometric_verified_skey
    from django.contrib.auth.models import User
    user = User.objects.get(id=int(user_id)) if user_id else None
    return face_mrz_or_nfc_verified_session_key(user, session_key) and pin_verified_skey(user, session_key) and biometric_verified_skey(user, session_key)

def get_next_redirect(request):
    if request.user.is_authenticated:
        from security.middleware import get_qs, redirect_path
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from security.tests import face_mrz_or_nfc_verified, pin_verified, biometric_verified
        red = False
        request.GET._mutable = True
        if request.user.is_authenticated and request.user.profile.vendor and (not request.path.startswith('/security/')) and (not request.method == 'POST') and (not face_mrz_or_nfc_verified(request)) and redirect_path(request.path):
            red = True
            request.GET._mutable = True
            request.GET['next'] = request.path + get_qs(request.GET)
            return HttpResponseRedirect(reverse('security:nfc') + get_qs(request.GET))
        if request.user.is_authenticated and request.user.profile.vendor and (not request.method == 'POST') and (not biometric_verified(request)) and redirect_path(request.path):
            red = True
            request.GET['next'] = request.path + get_qs(request.GET)
            return HttpResponseRedirect(reverse('security:biometric') + get_qs(request.GET))
        if request.user.is_authenticated and request.user.profile.vendor and (not request.method == 'POST') and (not pin_verified(request)) and redirect_path(request.path):
            red = True
            request.GET['next'] = request.path + get_qs(request.GET)
            return HttpResponseRedirect(reverse('security:pin') + get_qs(request.GET))
        if (not red) and (not request.method == 'POST') and redirect_path(request.path): sync_patch_session(request.user.id, request.session.session_key)
        return False
    return False
