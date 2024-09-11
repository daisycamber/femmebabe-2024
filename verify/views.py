from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse


def flow(request, uid):
    from verify.models import VeriFlow
    from django.http import HttpResponse
    import datetime, json
    from django.utils import timezone
    return HttpResponse(json.dumps({'success': VeriFlow.objects.filter(uid=uid, expires__gte=timezone.now() - datetime.timedelta(minutes=60*24*3).first().is_valid())}))

def flow_api(request):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument, VeriFlow
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    if not fraud_detect(request, False): return HttpResponse(403)
    input = json.loads(request.body)
    user = User.objects.filter(profile__idscan_api_key=input['key']).last()
    if not user.profile.idscan_active or user.profile.idscan_used > user.profile.idscan_plan: return HttpResponse(403)
    user.profile.idscan_used = user.profile.idscan_used + 1
    user.profile.save()
    next = input['next']
    flow = VeriFlow.objects.create(user=user, next=next)
    return HttpResponse(json.dumps({'adminurl': '{}{}'.format(settings.BASE_URL, reverse('verify:flow', kwargs={'uid': flow.uid})),'userurl': '{}{}'.format(settings.BASE_URL, user.profile.create_public_face_url() + '?next={}&flow={}'.format(next, flow.uid))}))

def api(request):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    if not fraud_detect(request, False): return HttpResponse(403)
    input = json.loads(request.body)
    user = User.objects.filter(profile__idscan_api_key=input['key']).last()
    if not user.profile.idscan_active or user.profile.idscan_used > user.profile.idscan_plan: return HttpResponse(403)
    user.profile.idscan_used = user.profile.idscan_used + 1
    user.profile.save()
    data = input['data']
    scan = DocumentScan.objects.create(user=user, side=input['side'])
    if input['side']:
        from barcode.idscantext import scan_ocr
        result = decode_ocr(data, instance)
    else:
        from verify.idscan import decode_barcode
        result = decode_barcode(data, instance)
    return HttpResponse(json.dumps({'result': result, 'data': DocumentScan.objects.get(id=scan.id).idscan}))

def get_timezone(ip):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    url = 'http://ip-api.com/json/' + ip
    req = urllib.request.Request(url)
    out = urllib.request.urlopen(req).read()
    o = json.loads(out)
    return o['timezone']

def handoff(request):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    logout(request)
    return HttpResponseRedirect(settings.REDIRECT_URL)

@login_required
def ofage_autocomplete(request):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    return 'y' if request.user.profile.identity_confirmed and request.COOKIES.get('age_verified') else 'n'

def ofage(request):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    if request.method == "POST":
        ip = get_client_ip(request)
        from security.apis import check_raw_ip_risk
        risk_detected = check_raw_ip_risk(ip, soft=False, dummy=False)
        if request.user.is_authenticated and not risk_detected:
            request.user.profile.identity_confirmed = True
            request.user.profile.save()
#            ip_obj = request.user.security_profile.ip_addresses.filter(ip_address=ip).first()
#            ip_obj.verified = True
#            ip_obj.save()
#        elif not risk_detected:
#            ip_obj = UserIpAddress.objects.filter(ip_address=ip, user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None).first()
#            ip_obj.verified = True
#            ip_obj.save()
        else:
            messages.warning(request, 'Please review the terms before continuing to use the app. Your internet address was flagged as high risk.')
            return HttpResponseRedirect(reverse('misc:terms'))
        messages.success(request, 'Thank you for verifying!')
        next_path = reverse('barcode:scan') + '?auth=t'
        next = request.GET.get('next','')
        qs = ''
        for key, value in request.GET.items():
            qs = qs + key + '=' + value + '&'
        response = None
        if next != '' and not (next.startswith('/accounts/logout/') or next.startswith('/accounts/login/') or next.startswith('/admin/login/') or next.startswith('/accounts/register/')):
            response = HttpResponseRedirect(next)
        elif next.startswith('/accounts/logout/') or next.startswith('/accounts/login/') or next.startswith('/accounts/register/'):
            response = HttpResponseRedirect(next_path)
        elif request.META.get('HTTP_REFERER', '/').startswith('/accounts/login/'):
            response = HttpResponseRedirect(next_path)
        elif not next:
            response = HttpResponseRedirect(next_path)
        else:
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        if not request.COOKIES.get('unax_verified', None):
            max_age = settings.VERIFY_UNAX_EXPIRATION_HOURS * 60 * 60
            expires = datetime.datetime.strftime(
                datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
                "%a, %d-%b-%Y %H:%M:%S GMT",
            )
            response.set_cookie('unax_verified', True, max_age=max_age, expires=expires)
        max_age = settings.VERIFY_AGE_EXPIRATION_HOURS * 60 * 60
        expires = datetime.datetime.strftime(
            datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
            "%a, %d-%b-%Y %H:%M:%S GMT",
        )
        response.set_cookie('age_verified', True, max_age=max_age, expires=expires)
        return response
    qs = ''
    for key, value in request.GET.items():
        qs = qs + '{}={}&'.format(key, value)
    post = Post.objects.filter(pinned=True, published=True, private=False, public=True).exclude(image=None).order_by('?').first()
    if not post: post = Post.objects.filter(published=True, private=False, public=True).exclude(image=None).order_by('?').first()
    while not post.get_image_thumb_url(): post = Post.objects.filter(published=True, private=False, public=True).exclude(image=None).order_by('?').first()
    return render(request, 'verify/ofage.html', {'hidenavbar': True, 'title': 'Confirm you are of age', 'small': True, 'showfooter': True, 'hide_logo': True, 'unax': request.COOKIES.get('unax_verified', None), 'the_qs': qs, 'post': post, 'min_age_adult': settings.MIN_AGE_ADULT})

@login_required
def verify(request):
    from django.shortcuts import render
    from django.urls import reverse
    from django.shortcuts import redirect
    import urllib, json
    import urllib.request
    from django.contrib.auth.decorators import login_required
    from django.contrib import messages
    import datetime
    from django.utils import timezone
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from .forms import VerificationForm
    from security.security import fraud_detect
    from users.tfa import send_user_text
    from .models import IdentityDocument
    from verify.models import IdentityDocument
    from django.contrib.auth.models import User
    from users.forms import get_past_date
    from security.models import UserIpAddress
    from users.views import check_username
    from security.apis import get_client_ip
    from feed.models import Post
    from django.conf import settings
    from .verify import validate_id
    from lotteh.celery import pend_id_verification
    if request.user.faces.count() == 0:
        messages.warning(request, 'Please take a photo of your face to continue.')
        return redirect(request.user.profile.create_face_url())
    if request.user.profile.identity_verified or request.user.profile.identity_verifying:
        return redirect(reverse('app:app'))
    if request.method == "POST":
        verification = None
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid() and not fraud_detect(request, True) and not request.user.profile.identity_verifying:
            form.instance.user = request.user
            if settings.ENABLE_AGECHECKER:
                uuid = request.POST.get("agechecker_uuid", '')
                url = 'https://api.agechecker.net/v1/status/' + uuid
                req = urllib.request.Request(url)
                out = urllib.request.urlopen(req).read()
                o = json.loads(out)
            v = request.user.verifications.last()
#            name_match = request.user.verifications.count() == 0 or not v or not v.full_name or form.instance.full_name == v.full_name
            name_match = check_username(form.instance.full_name)
            verification = form.save()
            user_verified = validate_id(verification)
            try:
                data = json.load(verification.idscan)
                result = data['ParseResult']
                document = result[list(result.keys())[0]]
                if document['LicenseNumber'] != verification.document_number and document['IDNumber'] != verification.document_number:
                    user_verified = False
                    messages.warning(request, 'Your identity could not be verified because the number you entered doesn\'t match the number on the document.')
                prev_scan = IdentityDocument.objects.filter(idscan=verification.idscan).last()
                if settings.USE_IDWARE and prev_scan and prev_scan.user and prev_scan.user != verification.user:
                    messages.warning(request, 'ID validation failed due to pre existing ID scan with name ' + prev_scan.user.username)
                    user_verified = False
                prev_scan = IdentityDocument.objects.filter(barcode_data=verification.barcode_data).last()
                if prev_scan and prev_scan.user != verification.user:
                    messages.success(request, 'ID validation failed due to pre existing ID scan with name ' + prev_scan.user.username)
                    user_verified = False
                prev_scan = IdentityDocument.objects.filter(document_number__icontains=verification.document_number).last()
                if settings.USE_IDWARE and prev_scan and prev_scan.user != verification.user:
                    messages.success(request, 'ID validation failed due to pre existing ID scan with name ' + prev_scan.user.username)
                    user_verified = False
                prev_scan = IdentityDocument.objects.filter(document_number__icontains=verification.document_number[:12]).last()
                if settings.USE_IDWARE and prev_scan and prev_scan.user != verification.user:
                    messages.success(request, 'ID validation failed due to pre existing ID scan with name ' + prev_scan.user.username)
                    user_verified = False
            except: pass
            print("Id validated? " + str(user_verified))
            p = request.user.profile
            if (not settings.ENABLE_AGECHECKER or o['status'] == 'accepted') and user_verified and name_match:
                send_user_text(User.objects.get(id=2), '{} has signed their documents for {}. They are a {} seeking {}. Please validate their pending identity verification, {}.'.format(p.name, settings.SITE_NAME, form.cleaned_data.get('i_am_a'), form.cleaned_data.get('seeking'), User.objects.get(id=2).profile.preferred_name))
                p.identity_verifying = True
                if request.user.profile.vendor:
                    p.identity_verifying = False
                    p.identity_verified = True
                else:
                    pend_id_verification.apply_async([request.user.id], countdown=settings.ID_VERIFICATION_COUNTDOWN)
                p.identity_verification_expires = timezone.now() + datetime.timedelta(days=settings.ID_VERIFICATION_EXPIRES_DAYS)
                p.save()
                verification.expire_date = timezone.now() + datetime.timedelta(days=settings.ID_VERIFICATION_EXPIRES_DAYS)
                verification.save()
                messages.success(request, 'Your identity has been verified. Please scan your ID and wait 24-72 hours for me to accept you.')
                return redirect(reverse('barcode:scan'))
            else:
                p.identity_verified = False
                p.identity_verification_failed = True
                p.save()
                messages.warning(request, 'Your identity verification failed. Please try again.')
                return redirect(request.path)
    prev_scan = IdentityDocument.objects.filter(user=request.user, verified=True).last()
    return render(request, 'verify/verify.html', {'title': 'Verify Your Age', 'medium': True, 'form': VerificationForm(initial={'full_name': prev_scan.full_name, 'birthday': prev_scan.birthday, 'document_number': prev_scan.document_number, 'address': prev_scan.address} if prev_scan else None), 'past_date': get_past_date().date, 'enable_agechecker': settings.ENABLE_AGECHECKER, 'securitymodal': False, 'securitymodaljs': False})
