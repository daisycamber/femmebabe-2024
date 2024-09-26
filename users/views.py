from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    UpdateView,
    DeleteView
)
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from face.tests import is_superuser_or_vendor
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page, never_cache, cache_control
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse


#@csrf_exempt
#@login_required
#@user_passes_test(is_superuser_or_vendor)
def google_auth(request):
    from django.shortcuts import redirect
    from users.oauth import get_auth_url
    import uuid
    url, state = get_auth_url(request, request.user.email if request.user.is_authenticated else None)
    print(state)
    request.session['state'] = state
    return redirect(url)

#@login_required
#@user_passes_test(is_superuser_or_vendor)

@csrf_exempt
def google_auth_callback(request):
    print(request.session.get('state'))
    from users.oauth import parse_callback_url
    from security.middleware import get_qs
    from django.shortcuts import redirect
    from django.conf import settings
    from django.urls import reverse
    authorization_code = None
    request.GET._mutable = True
#    get = dict(reversed(list(request.GET.items())))
    qs = '?'
    for key, val in request.GET.items():
        qs = qs + '{}={}&'.format(key, val)
    url = str(settings.BASE_URL + request.path + str(qs)).replace(' ', '+')[:-1]
    print(url)
    import json
    print('Request was {} to auth callback'.format(request.method))
    url = request.POST.get('auth')
    if url:
        email, token, refresh = parse_callback_url(request, url)
        print(email)
        from django.contrib.auth.models import User
        user = User.objects.filter(email=email).order_by('-profile__last_seen').last()
        if not user:
            from users.username_generator import generate_username as get_random_username
            user = User.objects.create_user(email=e, username=get_random_username(), password=get_random_string(length=8))
            if not hasattr(user, 'profile'):
                from users.models import Profile
                from security.models import SecurityProfile
                profile = Profile.objects.create(user=user)
                profile.finished_signup = False
                profile.save()
                security_profile = SecurityProfile.objects.create(user=user)
                security_profile.save()
            from django.contrib import messages
            messages.success(request, 'You are now subscribed, check your email for a confirmation. When you get the chance, fill out the form below to make an account.')
            from users.email import send_verification_email, sendwelcomeemail
            send_verification_email(user)
            send_registration_push(user)
            sendwelcomeemail(user)
        user.profile.token = token
        user.profile.refresh_token = refresh
        user.profile.save()
        from django.contrib.auth import login as auth_login
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        from django.contrib import messages
        messages.success(request, 'Successfully linked Google account')
        return redirect(reverse('/'))
    return render(request, 'users/oauth.html', {'title': 'Google Auth'})

def resolve_multiple_accounts(request, user):
    from .models import AccountLink
    if request.user.is_authenticated and not request.user.account_link:
        AccountLink.objects.create(from_user=request.user, to_user=user)

def password_reset(request, uidb64, token):
    from django.shortcuts import redirect, get_object_or_404
    from .forms import SetPasswordForm
    from django.contrib import messages
    from django.contrib.auth.models import User
    from django.utils.http import urlsafe_base64_decode
    user = get_object_or_404(User, id=urlsafe_base64_decode(uidb64))
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        from django.contrib.auth.tokens import default_token_generator
        if form.is_valid() and default_token_generator.check_token(user, token):
            user.profile.email_verified = True
            user.profile.finished_signup = True
            user.profile.save()
            user.save()
            form.save()
            messages.success(request, 'Your password has been reset.')
        elif not form.is_valid():
            messages.warning(request, 'Your passwords do not match, or do not meet the requirements. Please try again.')
            return redirect(request.path)
        else:
            messages.warning(request, 'Your password reset link has expired. Please create a new one.')
        return redirect(reverse('users:login'))
    from django.shortcuts import render
    return render(request, 'users/password_reset_confirm.html', {
        'title': 'Reset your Password',
        'form': SetPasswordForm(user)
    })

@csrf_exempt
@login_required
@user_passes_test(is_superuser_or_vendor)
def toggle_user_active(request, pk):
    from django.contrib.auth.models import User
    user = User.objects.get(id=pk)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
    return HttpResponse('<i class="bi bi-eye-fill"></i>' if user.is_active else '<i class="bi bi-eye-slash-fill"></i>')

@login_required
@user_passes_test(is_superuser_or_vendor)
def users(request):
    from django.shortcuts import render
    from django.contrib.auth.models import User
    from django.utils import timezone
    import datetime
    new_today = User.objects.filter(is_active=True, date_joined__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    new_this_month = User.objects.filter(is_active=True, date_joined__gte=timezone.now() - datetime.timedelta(hours=24*30)).count()
    subscribers = User.objects.filter(is_active=True, profile__subscribed=True).count()
    return render(request, 'users/users.html', {
        'title': 'All Accounts',
        'users': User.objects.all(),
        'new_today': new_today,
        'new_this_month': new_this_month,
        'subscribers': subscribers
    })


def logout_visitor(request):
    from django.contrib import messages
    from django.shortcuts import render
    from django.conf import settings
    if request.GET.get('message', None):
        messages.success(request, request.GET.get('message'))
    from django.contrib.auth import logout
    logout(request)
    return render(request, 'users/logout.html', {'small': True, 'title': 'You have been logged out of {}'.format(settings.SITE_NAME)})

def passwordless_login(request):
    from .forms import PhoneNumberForm
    from django.shortcuts import render, redirect, get_object_or_404
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        phone_number = form.data['phone_number'].replace('-', '').replace('(','').replace(')','')
        user = get_object_or_404(User, profile__phone_number=phone_number)
        if user.is_active:
            from users.tfa import send_user_text
            from django.contrib import messages
            send_user_text(user, 'Use the following link to log into your account: {}'.format(settings.BASE_URL) + user.profile.create_face_url() + ' - The link will expire in 3 minutes.')
            messages.success(request, 'A one time login link has been sent to your phone number, ' + phone_number + '.')
            return redirect(reverse('landing:landing'))
        else: messages.warning(request, 'This account is no longer active and login has been disabled.')
    form = PhoneNumberForm(initial={'phone_number': '+1'})
    return render(request, 'users/send_auth_text.html', {'title': 'Authenticate with a text', 'form': form, 'small': True})


def tfa(request, username, usertoken):
    from django.conf import settings
    from .forms import PhoneNumberForm
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.http import HttpResponseRedirect
    from .models import MFAToken
    from .forms import TfaForm
    from django.contrib.auth.models import User
    from django.utils import timezone
    from django.contrib import messages
    import datetime
    from django.core.exceptions import PermissionDenied
    token = MFAToken.objects.filter(uid=username, expires__gt=timezone.now() + datetime.timedelta(seconds=30)).order_by('-timestamp').last()
    if not token: token = MFAToken.objects.create(user=User.objects.filter(profile__uuid=username).first(), uid=username, expires=timezone.now() + datetime.timedelta(seconds=115))
    user = User.objects.filter(id=token.user.id).first()
    if not user and request.user.is_authenticated: return redirect(reverse('feed:home'))
    if not user: raise PermissionDenied()
    from django.contrib.auth import login as auth_login
    next = request.GET.get('next','')
    if not user.profile.enable_two_factor_authentication and user.is_active and user.profile.check_auth_token(usertoken, token):
        auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        user.profile.tfa_expires = timezone.now() + datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)
        user.profile.save()
        return HttpResponseRedirect(next if next != '' else reverse('landing:landing'))
    if not user.profile.tfa_enabled:
        from .tfa import check_verification_time
        if not check_verification_time(user, token):
            user.profile.tfa_enabled = False
            user.profile.enable_two_factor_authentication = True
            user.profile.phone_number = '+1'
            user.profile.save()
            print('Logging in user')
            resolve_multiple_accounts(request, user)
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.warning(request, 'Please enter a valid phone number and verify it with a code.')
            return redirect(reverse('users:tfa_onboarding'))
    from security.security import fraud_detect
    if request.method == 'POST' and not fraud_detect(request, True):
        form = TfaForm(request.POST)
        code = str(form.data.get('code', None))
        if code and code != '' and code != None:
            token_validated = user.profile.check_auth_token(usertoken)
            p = user.profile
            is_verified = False
#            try:
            from .tfa import check_verification_code
            is_verified = check_verification_code(user, token, code)
            print('Is verified?')
#            except:
#                is_verified = False
            p.tfa_authenticated = is_verified
            if token_validated:
                if is_verified:
                    user.profile.tfa_enabled = True
                    user.profile.save()
                    resolve_multiple_accounts(request, user)
                    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    face = user.faces.filter(session_key=None).last()
                    if face:
                        face.session_key = request.session.session_key
                        face.save()
                    p.tfa_expires = timezone.now() + datetime.timedelta(minutes=settings.LOGIN_VALID_MINUTES)
                    p.save()
                    messages.success(request, 'You have been authenticated. Welcome.')
                    qs = '?'
                    for key, value in request.GET.items():
                        qs = qs + key + '=' + value + '&'
                    if next != '' and not (next.startswith('/accounts/logout/') or next.startswith('/accounts/login/') or next.startswith('/admin/login/') or next.startswith('/accounts/register/')):
                        return HttpResponseRedirect(next)
                    elif next.startswith('/accounts/logout/') or next.startswith('/accounts/login/') or next.startswith('/accounts/register/'):
                        return redirect(reverse('/'))
                    elif request.META.get('HTTP_REFERER', '/').startswith('/accounts/login/'):
                        return redirect(reverse('/'))
                    elif not next:
                        return redirect(reverse('/'))
                    else:
                        return HttpResponseRedirect(reverse('verify:age') + '?next=' + request.META.get('HTTP_REFERER', '/'))
                else:
                    messages.warning(request, 'The code you entered was not recognized. Please try again.')
            elif not token_validated:
                messages.warning(request, 'The URL token has expired or was not recognized. Please try again.')
                from django.contrib.auth import logout
                logout(request)
                return redirect(reverse('users:login'))
            if p.tfa_attempts > 3:
                messages.warning(request, 'You have entered the incorrect code more than 3 times. please send yourself a new code.')
                p.verification_code = None
                p.save()
        elif user.profile.can_send_tfa < timezone.now():
            user.profile.tfa_attempts = 0
            user.profile.can_send_tfa = timezone.now() + datetime.timedelta(minutes=2)
            user.profile.save()
            from .tfa import send_verification_text, check_verification_code, send_user_text, send_text
            from .tfa import send_verification_email as send_tfa_verification_email
            if form.data.get('send_email', False):
                send_tfa_verification_email(user, token)
            else:
                send_verification_text(user, token)
            messages.success(request, "Please enter the code sent to your phone number or email. The code will expire in 3 minutes.")
        elif user.profile.can_send_tfa < timezone.now() + datetime.timedelta(seconds=115):
            messages.warning(request, 'You are sending too many two factor authentication codes. Wait a few minutes before sending another code.')
    form = TfaForm()
    hide_logo = None
    if user.profile.hide_logo:
        hide_logo = True
    if request.user.is_authenticated: return redirect(reverse('/'))
    return render(request, 'users/tfa.html', {'title': 'Enter Code', 'form': form, 'xsmall': True, 'user': user, 'hide_logo': hide_logo, 'accl_logout': user.profile.shake_to_logout, 'preload': False, 'autofocus': request.method == 'POST'})

@login_required
def tfa_onboarding(request):
    from .forms import PhoneNumberForm
    from django.shortcuts import redirect
    from django.contrib import messages
    if request.method == 'POST':
        form = PhoneNumberForm(request.POST)
        request.user.profile.phone_number = form.data['phone_number'].replace('-', '').replace('(','').replace(')','')
        request.user.profile.tfa_enabled = True
        request.user.profile.enable_two_factor_authentication = True
        request.user.profile.save()
        messages.success(request, 'You have added a phone number to your account.')
        user = request.user
        return redirect(user.profile.create_auth_url())
    form = PhoneNumberForm(initial={'phone_number': request.user.profile.phone_number if request.user.profile.phone_number else '+1'})
    from django.shortcuts import render
    return render(request, 'users/tfa_onboarding.html', {'title': 'Enter your phone number', 'form': form, 'small': True})

@never_cache
@login_required
def profile(request):
    oldusername = request.user.username
    p_form = None
    from .forms import UserUpdateForm, ProfileUpdateForm, NonVendorProfileUpdateForm
    from .models import Profile
    from django.contrib import messages
    from django.http import HttpResponse
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if request.user.profile.vendor:
            p_form = ProfileUpdateForm(request.POST,
                                       request.FILES,
                                       instance=request.user.profile)
        else:
            p_form = NonVendorProfileUpdateForm(request.POST,
                                       request.FILES,
                                       instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            d = Profile.objects.filter(user=request.user).values().first()
            d.update({'user': None, 'id': None, 'user_id': None})
            oldprofile = Profile(**d)
            newusername = p_form.data['name']
            uc = False
            if newusername != oldprofile.name:
                uc = check_username(newusername)
            if not uc and newusername != oldprofile.name:
                user = request.user
                user.profile.name = oldusername
                user.profile.save()
                messages.warning(request, f'Your username has not been accepted. Please select a more appropriate username.')
            elif not newusername: p_form.data['name'] = request.user.username
            new_phone_number = p_form.data['phone_number']
            u_form.save()
            profile = p_form.save(commit=False)
            profile.phone_number = profile.phone_number.replace('-', '').replace('(','').replace(')','')
            profile.save()
            if oldprofile.image != profile.image:
                from feed.align import face_rotation
                try:
                    rot = face_rotation(profile.image.path)
                    if rot == -1:
                        profile.rotate_right()
                    elif rot == 1:
                        profile.rotate_left()
                    profile.rotate_align()
                except: print("Failed to rotate profile photo")
            if new_phone_number != oldprofile.phone_number and oldprofile.phone_number and len(oldprofile.phone_number) >= 11:
                profile.tfa_enabled = True
                profile.save()
                send_text(oldprofile.phone_number, 'Your phone number has been updated to ' + new_phone_number + '. Please refer to texts on that phone to log in. If you didnt make this change, please call us. - {}'.format(settings.SITE_NAME))
            if profile.enable_two_factor_authentication and profile.phone_number and len(profile.phone_number) < 11:
                profile.enable_two_factor_authentication = False
                messages.success(request, f'Two factor authentication can\'t be activated without entering a phone number. Please enter a phone number to enable two factor authentication.')
            profile.save()
            if new_phone_number != oldprofile.phone_number and new_phone_number and len(new_phone_number) >= 11:
                send_user_text(request.user, 'You have added this number to {} for two factor authentication. You can now use your number for two factor authentication. If you didnt make this change, please call us. - {}'.format(settings.SITE_NAME, settings.DOMAIN))
                profile.tfa_enabled = True
                profile.tfa_code_expires = timezone.now() + datetime.timedelta(minutes=3)
                profile.save()
                return redirect(profile.create_auth_url())
            messages.success(request, f'Your profile has been updated!')
            print('Profile updated')
            return redirect('users:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        if request.user.profile.vendor:
            p_form = ProfileUpdateForm(instance=request.user.profile, initial={'phone_number': request.user.profile.phone_number if request.user.profile.phone_number else '+1'})
        else:
            p_form = NonVendorProfileUpdateForm(instance=request.user.profile, initial={'phone_number': request.user.profile.phone_number if request.user.profile.phone_number else '+1'})
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title':'Update Your Profile',
        'medium': True,
        'webpush_override': True
    }
    from django.shortcuts import render
    return render(request, 'users/profile.html', context)


def check_username(username):
    from profanity import profanity
    return not profanity.contains_profanity(username)

def check_username_old(username):
    from django.conf import settings
    import requests, json
    lang = 'en'
    data = {
        'text': username,
        'mode': 'standard',
        'lang': lang,
        'api_user': settings.SIGHTENGINE_USER,
        'api_secret': settings.SIGHTENGINE_SECRET
    }
    r = requests.post('https://api.sightengine.com/1.0/text/check.json', data=data)
    output = json.loads(r.text)
    try:
        if output['profanity']['matches'] or output['link']['matches']:
            return False
    except: return False
    return True

def set_user_cookie(response):
    import datetime
    max_age = 60 * 60 * 24 * 365
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    response.set_cookie('user_signup', True, max_age=max_age, expires=expires)
    return response


def send_registration_push(user):
    from pwa_webpush import send_user_notification
    from django.conf import settings
    from django.urls import reverse
    from django.contrib.auth.models import User
    payload = {
        'head': 'Someone new signed up with {}'.format(settings.SITE_NAME),
        'body': 'Meet the new visitor, @{}, on {}'.format(user.username, settings.SITE_NAME),
        'icon': settings.BASE_URL + settings.ICON_URL,
        'url': settings.BASE_URL + reverse('users:users'),
    }
    try:
        send_user_notification(User.objects.get(id=settings.MY_ID), payload=payload)
    except: pass

@cache_control(public=True)
def register(request):
    from security.apis import get_client_ip
    from django.contrib.auth.models import User
    from security.apis import check_raw_ip_risk
    from users.models import Profile
    from security.models import SecurityProfile
    from .email import send_verification_email, sendwelcomeemail
    from django.contrib import messages
    from users.username_generator import generate_username as get_random_username
    from security.apis import get_client_ip
    from email_validator import validate_email
    from .forms import UserRegisterForm
    from django.utils import timezone
    import datetime
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from security.security import fraud_detect
    import traceback
    from django.conf import settings
    ip = get_client_ip(request)
    e = request.GET.get('u', None)
    user = None
    if e:
        try:
            valid = validate_email(e, check_deliverability=True)
            us = User.objects.filter(email=e).last()
            safe = not check_raw_ip_risk(ip, soft=True, dummy=False, guard=True)
            if valid and not us and safe:
                user = User.objects.create_user(email=e, username=get_random_username(), password=get_random_string(length=8))
                if not hasattr(user, 'profile'):
                    profile = Profile.objects.create(user=user)
                    profile.finished_signup = False
                    profile.save()
                    security_profile = SecurityProfile.objects.create(user=user)
                    security_profile.save()
                messages.success(request, 'You are now subscribed, check your email for a confirmation. When you get the chance, fill out the form below to make an account.')
                send_verification_email(user)
                send_registration_push(user)
                sendwelcomeemail(user)
            elif us.profile.finished_signup and safe:
                user = us
                messages.warning(request, 'You already have an account with us. Please log in below.')
                response = redirect(reverse('users:login'))
                set_user_cookie(response)
                return response
            elif not valid: messages.warning(request, 'The email you entered is not valid or not deliverable.')
            else: messages.warning(request, 'You are using a risky IP address. Please do not continue.')
            user = us
        except: print(traceback.format_exc())
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        # user rate limit
        can_register = User.objects.filter(date_joined__date=datetime.date.today()).count() < settings.NEW_USERS_PER_DAY
        if can_register and form.is_valid() and not check_raw_ip_risk(ip, soft=True, dummy=False, guard=True):
            user = User.objects.filter(username=form.cleaned_data.get('username'), email=form.cleaned_data.get('email')).first()
            if not user:
                user = User.objects.filter(email=form.cleaned_data.get('email')).first()
            birthday = None
            try:
                birthday = datetime.datetime.strptime(form.data.get('birthday', ''), '%Y-%m-%d')
            except:
                birthday = datetime.datetime.strptime(form.data.get('birthday', ''), '%m/%d/%Y')
            if not birthday:
                messages.warning(request, 'Your birthday was not interpreted properly. Please enter in the format Year-Month-Day')
                return redirect(reverse('users:register'))
            from dateutil import relativedelta
            if birthday > datetime.datetime.now() - relativedelta(years=settings.MIN_AGE):
                messages.warning(request, 'You are not old enough to use this site. Please do not return until {}'.format((birthday + relativedelta(years=settings.MIN_AGE)).strftime("%B %d, %Y")))
                return redirect(reverse('app:app'))
            if User.objects.filter(username=form.cleaned_data.get('username'), profile__finished_signup=True).count() > 0 or User.objects.filter(email=form.cleaned_data.get('email'), profile__finished_signup=True).count() > 0:
                messages.warning(request, 'You are already registered. Please log in.')
                return redirect(reverse('users:login'))
            sendemail = False
            if not User.objects.filter(email=form.cleaned_data.get('email'), profile__finished_signup=True).first(): sendemail = True
            u = user
            if not u:
                u = User.objects.create(username=form.cleaned_data.get('username'), email=form.cleaned_data.get('email'))
            u.set_password(form.clean_password2())
            uc = check_username(u.username)
            if not uc:
                messages.warning(request, f'Your username has not been accepted. Please select a more appropriate username.')
                u.delete()
                return redirect(reverse('misc:terms'))
            profile = None
            if not hasattr(u, 'profile'):
                profile = Profile.objects.create(user=u)
                profile.save()
                security_profile = SecurityProfile.objects.create(user=u)
                security_profile.save()
            else:
                profile = u.profile
            profile.finished_signup = True
            profile.save()
            u.username = form.cleaned_data.get('username')
            u.save()
            if sendemail:
                send_verification_email(u)
                send_registration_push(u)
                sendwelcomeemail(u)
            messages.success(request, f'Your account has been created! Please check your email and verify your account.')
            response = redirect(reverse('verify:verify'))
            set_user_cookie(response)
            return response
        else:
            if not can_register:
                messages.warning(request, 'We have reached the limit of new accounts for the day. Please try to register again tomorrow.')
    else:
        arg = request.GET.get('u','')
        email = ''
        if not arg == '':
            email = arg
        if not email == '' and User.objects.filter(email=arg, profile__finished_signup=True).exists():
            messages.warning(request, f'You already have an account. Please log in instead.')
            return redirect(reverse('users:login'))
        elif email != '':
            messages.success(request, f'Please enter a username (can be your name) and a password, as well as check the box.')
        if user:
            form = UserRegisterForm(initial={'email': email})
        else:
            form = UserRegisterForm(initial={'email': email})
    import pytz
    available = settings.NEW_USERS_PER_DAY - User.objects.filter(date_joined__gte=datetime.datetime.combine(datetime.date.today() - datetime.timedelta(days=1), datetime.time(9,0)).astimezone(pytz.timezone(settings.TIME_ZONE))).count()
    from django.shortcuts import render
    response = render(request, 'users/register.html', {'form': form, 'title':'Register', 'dontshowad': True, 'dontshowsidebar': True, 'small': True, 'available_accounts': available, 'email_query_delay': 90})
    if user:
        response = set_user_cookie(response)
    return response

@cache_control(public=True)
def login(request):
    from django.conf import settings
    from security.apis import get_client_ip
    from django.contrib.auth.models import User
    from security.apis import check_raw_ip_risk, check_ip_risk
    from users.models import Profile
    from security.models import SecurityProfile, UserIpAddress
    from django.contrib import messages
    from users.username_generator import generate_username as get_random_username
    from security.apis import get_client_ip
    from email_validator import validate_email
    from django.contrib.auth.forms import AuthenticationForm
    import datetime
    from django.shortcuts import render, redirect, get_object_or_404
    from django.urls import reverse
    from django.utils import timezone
    from security.security import fraud_detect
    from django.contrib.auth import login as auth_login
    from security.models import UserLogin
    ip = get_client_ip(request)
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        the_user = None
        try:
            the_user = User.objects.get(username=username)
        except:
            the_user = None
        user = None
        disable_login = False
        if the_user:
            if not hasattr(the_user, 'security_profile'):
                SecurityProfile.objects.create(user=the_user)
            if not hasattr(the_user, 'profile'):
                Profile.objects.create(user=the_user)
            ip_objs = the_user.security_profile.ip_addresses.filter(ip_address=ip)
            if (ip_objs.first() and ip_objs.first().risk_detected) or not the_user.is_active:
                disable_login = True
                messages.warning(request, 'Your account has been disabled.')
        print(disable_login)
        if hasattr(the_user, 'profile') and the_user.user_logins.filter(timestamp__lte=timezone.now(), timestamp__gte=timezone.now() - datetime.timedelta(seconds=15)).count() <= 5 and not disable_login:
            from django.contrib.auth import authenticate, logout
            user = authenticate(username=username,password=password)
            UserLogin.objects.create(user=user)
            print(user)
            if not user and the_user:
                the_user.profile.save()
            else: print('successful login for user {}'.format(username))
        else: print('login rate limited for {}'.format(username))
        if user and hasattr(user, 'profile'):
            if hasattr(user, 'security_profile'):
                p = user.security_profile
                profile = user.profile
                if not ip in user.security_profile.ip_addresses.values_list('ip_address', flat=True):
                    ip_address = UserIpAddress()
                    ip_address.user = user
                    ip_address.ip_address = ip
                    ip_address.save()
                    ip_address.page_loads = 1
                    ip_address.risk_detected = check_ip_risk(ip_address, soft=True, dummy=False)
                    ip_address.save()
                    p.ip_addresses.add(ip_address)
                    p.save()
                ip_obj = user.security_profile.ip_addresses.filter(ip_address=ip).first()
                ip_obj.page_loads = ip_obj.page_loads + 1
                ip_obj.risk_detected = check_ip_risk(ip_obj)
                ip_obj.save()
                p = profile
                risk_detected = ip_obj.risk_detected
            if not hasattr(user, 'profile'):
                profile = Profile.objects.create(user=user)
                profile.save()
            if user.is_active and user.profile.email_verified and user.user_logins.filter(timestamp__lte=timezone.now(), timestamp__gte=timezone.now() - datetime.timedelta(seconds=15)).count() <= 2:
                user.profile.can_login = timezone.now() - datetime.timedelta(seconds=15)
                user.profile.save()
                messages.success(request, f'Welcome back to ' + settings.SITE_NAME + ', ' + user.profile.preferred_name + '.' + (' Please complete authentication.' if user.profile.enable_two_factor_authentication else ''))
                profile = user.profile
                profile.verification_code = None
                profile.save()
                next = request.GET.get('next', '')
                extra = ''
                qs = '?'
                for key, value in request.GET.items():
                    qs = qs + key + '=' + value + '&'
                if not profile.enable_facial_recognition_bypass:
                    response = redirect(user.profile.create_face_url() + qs)
                elif not user.profile.enable_two_factor_authentication:
                    from users.logout import logout_user
                    if settings.LIMIT_BYPASS_LOGIN: logout_user(user)
                    resolve_multiple_accounts(request, user)
                    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    response = redirect(reverse('app:app'))
                else:
                    response = redirect(user.profile.create_auth_url() + qs)
                response = set_user_cookie(response)
                return response
            elif not the_user.profile.email_verified:
                messages.warning(request, f'You tried to log in to your account, but have not yet verified your email. Please follow the link in your email to log in to your account, or request a new link by clicking the button below and entering your email. <a href="' + reverse('users:resend_activation') + '" title="Resend activation email">Resend Activation Email</a>')
                return redirect(reverse('users:verify'))
            else:
                messages.warning(request, 'You are trying to log in too much. Please wait another {} seconds before logging in.'.format(str((the_user.profile.can_login - timezone.now()).seconds)))
                return redirect(reverse('users:login'))
        else:
            messages.warning(request, 'Your username or password is not correct, or you are trying to log in too much. Please wait another {} seconds before logging in.'.format(str((the_user.profile.can_login - timezone.now()).seconds) if the_user else 'few'))
            return redirect(reverse('users:login'))
    else:
        form = AuthenticationForm()
    title = 'Login'
    if request.GET.get('next', None):
        title = 'Log in to visit ' + request.GET.get('next', '')
    return render(request,'users/login.html', {'form':form, 'title': title, 'dontshowad': True, 'dontshowsidebar': True, 'small': True, 'email_query_delay': 15})

def activate(request, uidb64, token):
    from django.contrib import messages
    from django.contrib.auth.models import User
    from security.apis import get_client_ip
    from security.apis import check_raw_ip_risk
    from .email import sendwelcomeemail
    from django.shortcuts import redirect
    from django.conf import settings
    from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
    from .tokens import account_activation_token
    from django.utils.encoding import force_str
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    ip = get_client_ip(request)
    if user is not None and account_activation_token.check_token(user, token) and not check_raw_ip_risk(ip):
        if not user.profile.email_verified:
            from .tfa import send_user_text
            send_user_text(User.objects.get(id=settings.MY_ID), 'Someone new has joined {}.'.format(settings.SITE_NAME))
        user.profile.email_verified = True
        user.profile.finished_signup = True
        user.profile.save()
        user.save()
        sendwelcomeemail(request, user)
        messages.success(request, f'Thanks for confirming your email! You can now log into your account, and a welcome email has been sent to you.')
        return redirect(user.profile.create_face_url())
    else:
        messages.success(request, f'Your activation link has expired. Please request a new activation link.')
        return redirect('verify:verify')

def resend_activation(request):
    from .forms import ResendActivationEmailForm
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        email = request.POST['email']
        from django.contrib import messages
        from django.urls import reverse
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(email=email)
            from .email import send_verification_email
            send_verification_email(user)
            messages.success(request,'Your verification email sent. Please click the link in your email to verify your account.')
            return redirect(reverse('verify:verify'))
        except:
            messages.warning(request,f'Your email is not correct. Please try again.')
    else:
        form = ResendActivationEmailForm()
    from django.shortcuts import render
    return render(request,'users/resend_activation.html',{'form': form, 'title': 'Resend Activation', 'small': True})

#@cache_page(60*60*24*30*12)
def verify(request):
    from django.shortcuts import render
    return render(request, 'users/verify.html',{'title': 'Verify your email', 'small': True})

def unsubscribe(request, username, token):
    from django.urls import reverse
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    from django.contrib.auth.models import User
    user = User.objects.filter(username=username).first()
    if not user: user = get_object_or_404(User, profile_uuid=username)
    if request.method == 'POST' and ((request.user.is_authenticated and request.user == user) or user.profile.check_token(token)):
        profile = user.profile
        profile.subscribed = not profile.subscribed
        profile.save()
        messages.success(request, 'You have been {}'.format('resubscribed.' if profile.subscribed else 'unsubscribed.'))
        from django.shortcuts import redirect
        return redirect(reverse('app:app'))
    if request.method == 'GET' and ((request.user.is_authenticated and request.user == user) or user.profile.check_token(token)):
        # unsubscribe them
        profile = user.profile
        profile.subscribed = False
        profile.save()
        from django.shortcuts import render
        return render(request, 'users/unsubscribe.html', {'title': 'Unsubscribe', 'link': user.profile.create_unsubscribe_link()})
    # Otherwise redirect to login page
    from django.http import HttpResponseRedirect
    messages.warning(request,f'Your unsubscribe link has expired. Please log in to unsubscribe.')
    next_url = reverse('users:unsubscribe', kwargs={'username': username, 'token': token,})
    return HttpResponseRedirect('%s?next=%s' % (reverse('login'), next_url))


from django.contrib.auth.models import User

class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    success_url = '/'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def test_func(self):
        user = self.get_object()
        if self.request.user != user and self.request.user.is_superuser:
            return True
        return False
