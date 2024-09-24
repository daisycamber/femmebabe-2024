from django.contrib.auth.decorators import user_passes_test
from .tests import recent_face_match
from vendors.tests import is_vendor
from feed.tests import identity_verified
from webauth.decorators import webauth_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .tests import face_mrz_or_nfc_verified, recent_face_match, pin_verified, request_passes_test, biometric_verified
from face.tests import is_superuser_or_vendor
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

current_challenges = {}

@login_required
@user_passes_test(is_superuser_or_vendor)
def webauth_begin(request):
    from .models import Biometric
    from django.shortcuts import redirect
    if biometric_verified(request): return redirect(request.GET.get('next') if request.GET.get('next') else '/')
    if not biometric_verified(request) and not request.session.get('webauth_device_id', None):
        return redirect('/webauth/verify/?next=/security/biometric/?next=' + request.GET.get('next', '/'))
    return redirect(request.GET.get('next', '/'))

#@webauth_required
@login_required
@user_passes_test(is_superuser_or_vendor)
def webauth_redirect(request):
    from .models import Biometric
    from django.shortcuts import redirect
    if biometric_verified(request): return redirect(request.GET.get('next') if request.GET.get('next') else '/')
    if not request.session.get('webauth_device_id', None) and not request.user.webauth_devices.count() == 0:
        return redirect('/webauth/verify/?next=/security/biometric/?next=' + request.GET.get('next', '/'))
    Biometric.objects.create(user=request.user, session_key=request.session.session_key)
    request.user.profile.enable_biometrics = True
    request.user.profile.save()
    request.session["webauth_device_id"] = None
    request.session.save()
    return redirect(request.GET.get('next') if request.GET.get('next') else '/')

@csrf_exempt
@login_required
@user_passes_test(is_superuser_or_vendor)
def webauth(request):
    from django.shortcuts import render
    from webauthn import generate_registration_options, generate_authentication_options, options_to_json, verify_registration_response, verify_authentication_response
    from webauthn.helpers.structs import (
        AuthenticatorSelectionCriteria,
        UserVerificationRequirement,
        RegistrationCredential,
        AuthenticationCredential,
    )
    from django.http import HttpResponse
    if request.method == 'GET':
        if not request.user.biometric.count() > 0 and not request.GET.get('register', False): return redirect(request.path + '?register=t&next=' + (request.GET.get('next') if request.GET.get('next') else '/'))
        return render(request, 'security/webauth.html', {'title': 'Biometric Authentication', 'securitymodal': False, 'securitymodaljs': False})
    global current_challenges
    logged_in_user_id = bytes(str(request.user.id), 'utf-8')
    if request.GET.get('auth', False):
        current_challenge = current_challenges[logged_in_user_id]
        verification = None
        try:
            credential_data = json.loads(request.body)
            print(json.dumps(credential_data))
            for _cred in user.credentials.all():
                try:
                    verification = verify_authentication_response(
                        credential=credential_data,
                        expected_challenge=current_challenge,
                        expected_rp_id=settings.DOMAIN,
                        expected_origin=settings.BASE_URL,
                        credential_public_key=user_credential.public_key,
                        credential_current_sign_count=user_credential.sign_count,
                        require_user_verification=True,
                    )
                except: pass
        except Exception as err:
            import traceback
            print(traceback.format_exc())
            return HttpResponse(str(err))
        if not verification: return HttpResponse('This credential is not verified.')
        Biometric.objects.create(user=request.user, session_key=request.session.session_key)
        return HttpResponse('v')
    if request.GET.get('verify', False):
        current_challenge = current_challenges[logged_in_user_id]
        verification = None
        try:
            credential_data = json.loads(request.body)
            verification = verify_registration_response(
                credential=credential_data,
                expected_challenge=current_challenge,
                expected_rp_id=settings.DOMAIN,
                expected_origin=settings.BASE_URL,
                require_user_verification=True,
            )
        except Exception as err:
            import traceback
            print(traceback.format_exc())
            return HttpResponse(str(err))
        new_credential = Credential.objects.create(
            user=request.user,
            bin_id=verification.credential_id,
            public_key=verification.credential_public_key.tobytes(),
            sign_count=verification.sign_count,
            transports=json.dumps(json.loads(request.body).get("transports", [])),
            name=request.GET.get('name', ''),
        )
        Biometric.objects.create(user=request.user, session_key=request.session.session_key)
        return HttpResponse('v')
    if request.GET.get('register', False):
        options = generate_registration_options(
            rp_name=settings.SITE_NAME,
            rp_id=settings.DOMAIN,
            user_id=logged_in_user_id,
            user_name=request.user.username,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
        current_challenges[logged_in_user_id] = options.challenge
        options_json = options_to_json(options)
        return HttpResponse(str(options_json))
    from collections import namedtuple
    allow = []
    for cred in request.user.credentials.all():
        dictionary = {"value": "public-key"}
        type = namedtuple('Struct', dictionary.keys())(*dictionary.values())
        dictionary = {"value": cred.transports}
        transports = namedtuple('Struct', dictionary.keys())(*dictionary.values())
        dictionary = {"type": type, "id": cred.bin_id.tobytes(), "transports": transports}
        allow = allow + [namedtuple('Struct', dictionary.keys())(*dictionary.values())]
    options = generate_authentication_options(
        rp_id=settings.DOMAIN,
        user_verification=UserVerificationRequirement.REQUIRED,
        allow_credentials=allow,
    )
    current_challenges[logged_in_user_id] = options.challenge
    options_json = options_to_json(options)
    return HttpResponse(str(options_json))

@csrf_exempt
@login_required
@user_passes_test(is_superuser_or_vendor)
def approve_login(request, id):
    from security.models import UserSession
    from django.http import HttpResponse
    login = UserSession.objects.filter(id=id).first()
    if request.method == 'POST' and login:
        login.bypass = True
        login.save()
    return HttpResponse('<i class="bi bi-door-open-fill"></i>')

@login_required
@user_passes_test(is_superuser_or_vendor)
def logins(request):
    from .models import UserSession
    from django.shortcuts import render
    from django.utils import timezone
    import datetime
    from django.conf import settings
    the_logins = UserSession.objects.filter(bypass=False, user=request.user, timestamp__gte=timezone.now() - datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)).order_by('-timestamp')
    return render(request, 'security/bypass.html', {
        'title': 'Approve Logins',
        'logins': list(the_logins)[:32]
    })

def scan_barcode(path):
#    from docbarcodes.extract import process_document
#    barcodes_raw, barcodes_combined = process_document(path)
#    print(barcodes_raw)
    import zxing, re
    reader = zxing.BarCodeReader()
    barcode = str(reader.decode(path))
    matches = re.findall("raw='([^']+)'", str(barcode))
    fmatch = re.findall("format='([\\w+]+)'", str(barcode))
    if not 'PDF_417' in fmatch:
        print(fmatch)
        return False
    match = ''
    for m in matches:
        print(m)
        if len(m) > len(match):
            match = m
    return match

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
#@user_passes_test(recent_face_match)
def set_pincode(request):
    from .forms import PincodeForm
    if request.method == 'POST':
        from django.shortcuts import redirect
        form = PincodeForm(request.POST)
        if form.is_valid(): # and recent_face_match(request):
            if not str(form.cleaned_data.get('pin')) != '':
                from django.contrib import messages
                messages.warning(request, 'No pin was entered.')
                return redirect(request.path)
            p = request.user.security_profile
            p.pincode = str(form.cleaned_data.get('pin'))
            p.save()
            from django.contrib import messages
            messages.success(request, 'Your pin has been accepted.')
            return redirect(request.GET.get('next') if request.GET.get('next') else '/')
    from django.shortcuts import render
    return render(request, 'security/pin.html', {'title': 'Enter Pin', 'form': PincodeForm()})

@login_required
def pincode(request):
    from security.tests import pin_verified
    from django.shortcuts import redirect
    from django.urls import reverse
    if not request.user.security_profile.pincode or pin_verified(request): return redirect(request.GET.get('next') if request.GET.get('next') else reverse('/'))
    from .forms import PincodeForm
    if request.method == 'POST':
        form = PincodeForm(request.POST)
        if form.is_valid():
            from django.shortcuts import redirect
            from django.contrib import messages
            from django.utils import timezone
            p = request.user.security_profile
            if not str(form.cleaned_data.get('pin')) == request.user.security_profile.pincode and not timezone.now() < p.pin_entered_incorrectly:
                messages.warning(request, 'This pincode was not correct.')
                p.incorrect_pin_attempts = p.incorrect_pin_attempts + 1
                if p.incorrect_pin_attempts > 3:
                    p.pin_entered_incorrectly = timezone.now() + datetime.timedelta(minutes=3)
                p.save()
                return redirect(request.path)
            p.pin_entered = timezone.now()
            p.incorrect_pin_attempts = 0
            p.save()
            from .models import Pincode
            Pincode.objects.create(user=request.user, session_key=request.session.session_key)
            messages.success(request, 'Your pin has been accepted.')
            return redirect(request.GET.get('next') if request.GET.get('next') else '/')
    from django.shortcuts import render
    return render(request, 'security/pin.html', {'title': 'Enter Pin', 'form': PincodeForm(), 'securitymodal': False, 'securitymodaljs': False})

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def modal(request):
    from django.http import HttpResponse
#    if request.method == 'POST':
    return HttpResponse('y' if face_mrz_or_nfc_verified(request) else 'n')
#    else: return HttpResponse('n')

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def shake(request):
    if request.method == 'POST':
        for scan in request.user.mrz_scans.filter(valid=True, timestamp__gte=timezone.now()-datetime.timedelta(minutes=settings.MRZ_SCAN_REQUIRED_MINUTES)):
            scan.valid = False
            scan.save()
        for scan in request.user.nfc_scans.filter(valid=True, timestamp__gte=timezone.now()-datetime.timedelta(minutes=settings.NFC_SCAN_REQUIRED_MINUTES)):
            scan.valid = False
            scan.save()
    return HttpResponse(200)

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
#@user_passes_test(recent_face_match)
def scan_mrz(request):
    from pdf417 import encode, render_image
    from .models import MRZScan
    from django.http import HttpResponse
    from .forms import MRZScanForm
    from django.utils.crypto import get_random_string
    from django.conf import settings
    scan = None
    ocr_key = None
    if request.GET.get('generate', False) and face_mrz_or_nfc_verified(request):
        barcode_data = get_random_string(length=settings.VERIFICATION_MRZ_LENGTH)
        ocr_key = get_random_string(length=settings.VERIFICATION_OCR_LENGTH)
        scan = MRZScan.objects.create(user=request.user, barcode_data=barcode_data)
        path = os.path.join(settings.MEDIA_ROOT, get_document_path(scan, 'scan.jpg'))
        codes = encode(barcode_data, columns=2)
        image = render_image(codes, scale=5)
        image.save(path)
        scan.ocr_key = ocr_key
        scan.image = path
        scan.save()
    if request.method == 'POST':
        form = MRZScanForm(request.POST, request.FILES)
        if form.is_valid():
            from verify.ocr import get_image_text
            from verify.forensics import text_has_valid_birthday_and_expiry, text_has_valid_expiry, text_matches_name
            form.instance.user = request.user
            scan = form.save()
            data = scan_barcode(scan.image.path)
            verified = data and MRZScan.objects.filter(user=request.user, barcode_data=data).count() > 0
            scan.barcode_data = data
            scan.session_key = request.session.session_key
            scan.ocr_data = get_image_text(scan.image.path)
            scan.save()
            ocr_verified = False
            for key in MRZScan.objects.exclude(ocr_key='').values_list('ocr_key', flat=True).distinct():
                if key in scan.ocr_data:
                    ocr_verified = True
                    break;
            ocr_valid = (text_has_valid_birthday_and_expiry(scan.ocr_data) if request.user.verifications.last() else text_has_valid_expiry(scan.ocr_data) and text_matches_name(scan.ocr_data, request.user.verifications.last().full_name if request.user.verifications.last() else request.user.profile.name))
            verified = verified and ocr_verified and ocr_valid
            if not verified: scan.delete()
            return HttpResponse('y' if verified else 'n')
    from django.utils import timezone
    import datetime
    return render(request, 'security/mrz.html', {
        'title': 'Scan MRZ',
        'form': MRZScanForm(),
        'scan': scan,
        'key': ocr_key,
        'birthday_and_expiry': request.user.verifications.last().birthday.strftime('%m/%d/%Y') if request.user.verifications.last() else timezone.now().strftime('%m/%d/%Y') + ' - ' + (timezone.now() + datetime.timedelta(days=183)).strftime('%m/%d/%Y')
    })

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
#@user_passes_test(recent_face_match)
def scan_nfc(request):
    from django.utils.crypto import get_random_string
    from .models import NFCScan
    from .forms import NFCScanForm
    from django.conf import settings
    from django.http import HttpResponse
    if request.method == 'POST':
        form = NFCScanForm(request.POST)
        if form.is_valid():
            from security.crypto import decrypt
            import urllib.parse
            id = None
            data = None
            try:
                id = urllib.parse.unquote(form.cleaned_data.get('nfc_id'))
                print(id)
                try:
                    data = urllib.parse.unquote(form.cleaned_data.get('nfc_data'))
                except: data = None
                form.instance.nfc_id = decrypt(id, settings.PUB_AES_KEY)
                form.instance.nfc_data = decrypt(data, settings.PUB_AES_KEY) if form.cleaned_data.get('nfc_data', None) else None
            except:
                id = form.cleaned_data.get('nfc_id')
                data = form.cleaned_data.get('nfc_data')
                form.instance.nfc_id = decrypt(id, settings.PUB_AES_KEY)
                form.instance.nfc_data = decrypt(data, settings.PUB_AES_KEY) if form.cleaned_data.get('nfc_data', None) else None
            print(form.instance.nfc_id)
            allowed = NFCScan.objects.filter(user=request.user).count() == 0 or (NFCScan.objects.filter(user=request.user, nfc_id=form.instance.nfc_id, valid=True).count() > 0) or (request.GET.get('generate', False) and face_mrz_or_nfc_verified(request))
            if not allowed: return HttpResponse('n')
            form.instance.user = request.user
            form.instance.session_key = request.session.session_key
            scan = form.save()
            return HttpResponse('y')
    from django.shortcuts import render
    from django.urls import reverse
    return render(request, 'security/nfc.html', {
        'title': 'Scan NFC',
        'form': NFCScanForm(),
        'nfc_data': get_random_string(length=settings.VERIFICATION_NFC_LENGTH),
        'session_key': request.session.session_key,
        'base_url': settings.BASE_URL,
        'towrite_url': settings.BASE_URL + reverse('payments:buy-photo-card', kwargs={'username': request.user.profile.name}) + '?coupon=' + settings.COUPON_CODE, #settings.STATIC_SITE_URL,
        'pub_aes_key': settings.PUB_AES_KEY,
        'rel_aes_key': settings.REL_AES_KEY
    })



def all_unexpired_sessions_for_user(user):
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    user_sessions = []
    all_sessions  = Session.objects.filter(expire_date__gte=timezone.now())
    for session in all_sessions:
        session_data = session.get_decoded()
        try:
            if user.id == int(session_data.get('_auth_user_id')):
                user_sessions.append(session.pk)
        except: pass
    return Session.objects.filter(pk__in=user_sessions)

def delete_all_unexpired_sessions_for_user(user, session_to_omit=None):
    session_list = all_unexpired_sessions_for_user(user)
    if session_to_omit is not None:
        session_list.exclude(session_key=session_to_omit.session_key)
    session_list.delete()


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def logout_everyone(request):
    if not (request.user.profile.admin or request.user.is_superuser):
        return redirect(reverse('landing:landing'))
    from security.secure import secure_remove_dir
    secure_remove_dir('secure/media/')
    secure_remove_dir('secure/video/')
    for user in User.objects.all():
        delete_all_unexpired_sessions_for_user(user)
        user.profile.tfa_authenticated = False
    return redirect(reverse('landing:landing'))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def logout_everyone_but_user(request):
    from django.urls import reverse
    from django.shortcuts import redirect
    from django.contrib.auth.models import User
    from security.secure import secure_remove_dir
    if not (request.user.profile.admin or request.user.is_superuser):
        return redirect(reverse('landing:landing'))
    secure_remove_dir('secure/media/')
    secure_remove_dir('secure/video/')
    for user in User.objects.all():
        if user != request.user:
            delete_all_unexpired_sessions_for_user(user)
            user.profile.tfa_authenticated = False
    return redirect(reverse('landing:landing'))
