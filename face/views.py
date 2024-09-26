from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from .tests import is_superuser_or_vendor
from django.views.decorators.csrf import csrf_exempt

def get_face_path(instance, filename):
    import uuid, os
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('face/', filename)

@login_required
#@user_passes_test(is_superuser_or_vendor)
def secure_photo(request, filename):
    from django.urls import reverse
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.models import User
    from users.models import Profile
    from .forms import FaceForm
    #from lotteh.celery import face_id_task
    from .models import Face, FaceToken
    from django.contrib import messages
    from django import forms
    from django.http import HttpResponse, HttpResponseRedirect
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import base64
    import io, os
    import base64, uuid
    from django.utils.crypto import get_random_string
    from django.contrib.auth import login
    from security.models import UserIpAddress
    from security.middleware import get_client_ip
    import traceback
    from security.apis import check_ip_risk, get_client_ip
    from security.models import UserIpAddress
    from django.contrib.auth import logout
    from security.middleware import FRAUD_MOD
    import datetime, pytz
    from django.utils import timezone
    from django.conf import settings
    from stacktrace.exceptions import FaceLoginFailedException
    from security.middleware import get_uuid
    from feed.middleware import set_current_exception
    from django.core.exceptions import PermissionDenied
    from security.security import fraud_detect
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    u = int(filename.split('.')[0].split('-')[-1])
    if u != request.user.id:
        raise PermissionDenied()
    image_data = open(os.path.join(settings.BASE_DIR, 'media/secure/face/', filename), "rb").read()
    ext = filename.split('.')[1]
    return HttpResponse(image_data, content_type="image/{}".format(ext))

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def all_faces(request):
    from django.urls import reverse
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.models import User
    from users.models import Profile
    from .forms import FaceForm
    #from lotteh.celery import face_id_task
    from .models import Face, FaceToken
    from django.contrib import messages
    from django import forms
    from django.http import HttpResponse, HttpResponseRedirect
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import base64
    import io, os
    import base64, uuid
    from django.utils.crypto import get_random_string
    from django.contrib.auth import login
    from security.models import UserIpAddress
    from security.middleware import get_client_ip
    import traceback
    from security.apis import check_ip_risk, get_client_ip
    from security.models import UserIpAddress
    from django.contrib.auth import logout
    from security.middleware import FRAUD_MOD
    import datetime, pytz
    from django.utils import timezone
    from django.conf import settings
    from stacktrace.exceptions import FaceLoginFailedException
    from security.middleware import get_uuid
    from feed.middleware import set_current_exception
    from django.core.exceptions import PermissionDenied
    from security.security import fraud_detect
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    theuser = User.objects.filter(profile__name=request.GET.get('model')).first()
    if not theuser: theuser = request.user
    else:
        if not theuser in request.user.profile.subscriptions.all() and not request.user == theuser:
            raise PermissionDenied()
    faces = Face.objects.filter(user=theuser, authentic=True).order_by('timestamp')
    if theuser == request.user and request.GET.get('all', None):
        faces = Face.objects.filter(user=theuser).order_by('timestamp')
    return render(request, 'face/faces.html', {'faces': faces})

@csrf_exempt
def auth_url(request, username, token):
    from django.urls import reverse
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.models import User
    from users.models import Profile
    from .forms import FaceForm
    #from lotteh.celery import face_id_task
    from .models import Face, FaceToken
    from django.contrib import messages
    from django import forms
    from django.http import HttpResponse, HttpResponseRedirect
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import base64
    import io, os
    import base64, uuid
    from django.utils.crypto import get_random_string
    from django.contrib.auth import login
    from security.models import UserIpAddress
    from security.middleware import get_client_ip
    import traceback
    from security.apis import check_ip_risk, get_client_ip
    from security.models import UserIpAddress
    from django.contrib.auth import logout
    from security.middleware import FRAUD_MOD
    import datetime, pytz
    from django.utils import timezone
    from django.conf import settings
    from stacktrace.exceptions import FaceLoginFailedException
    from security.middleware import get_uuid
    from feed.middleware import set_current_exception
    from django.core.exceptions import PermissionDenied
    from security.security import fraud_detect
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    if True: #request.method == 'POST':
        try:
            user = User.objects.filter(profile__uuid=username).order_by('-profile__last_seen').first()
            face = Face.objects.get(token=token)
#            print(face.authorized)
            if not face.token == '' and not username == '' and not face.auth_url == '':
                face.authorized = True
                face.save()
                return HttpResponse(face.auth_url)
            else: return HttpResponse('none')
        except:
            return HttpResponse('failed')
    return HttpResponse('none')

@csrf_exempt
def face_verify(request, username, token):
    from verify.models import VeriFlow
    from django.urls import reverse
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.models import User
    from users.models import Profile
    from .forms import FaceForm
    #from lotteh.celery import face_id_task
    from .models import Face, FaceToken
    from django.contrib import messages
    from django import forms
    from django.http import HttpResponse, HttpResponseRedirect
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import base64
    import io, os
    import base64, uuid
    from django.utils.crypto import get_random_string
    from django.contrib.auth import login
    from security.models import UserIpAddress
    from security.middleware import get_client_ip
    import traceback
    from security.apis import check_ip_risk, get_client_ip
    from security.models import UserIpAddress
    from django.contrib.auth import logout
    from security.middleware import FRAUD_MOD
    import datetime, pytz
    from django.utils import timezone
    from django.conf import settings
    from stacktrace.exceptions import FaceLoginFailedException
    from security.middleware import get_uuid
    from feed.middleware import set_current_exception
    from django.core.exceptions import PermissionDenied
    from security.security import fraud_detect
    from django.contrib.auth.models import User
    from django.utils.crypto import get_random_string
    flow = None
    token = FaceToken.objects.filter(uid=username).order_by('-timestamp').last()
    if not token: token = FaceToken.objects.create(user=User.objects.filter(profile__uuid=username).first(), uid=username, expires=timezone.now() + datetime.timedelta(seconds=115))
    user = User.objects.filter(id=token.user.id).first()
    if request.GET.get('flow', False): flow = VeriFlow.objects.filter(uid=request.GET.get('flow', None), expires__gte=timezone.now()-datetime.timedelta(minutes=15))
    if not flow and not user: return redirect(reverse('users:login'))
    if flow:
        user = None
    ip = get_client_ip(request)
#    if not user:
#        return redirect(reverse('users:login'))
    if user and hasattr(user, 'security_profile'):
        p = user.security_profile
        if not ip in user.security_profile.ip_addresses.values_list('ip_address', flat=True):
            ip_address = UserIpAddress()
            ip_address.user = user
            ip_address.ip_address = ip
            ip_address.save()
            ip_address.page_loads = 1
            ip_address.risk_detected = check_ip_risk(ip_address)
            ip_address.save()
            p.ip_addresses.add(ip_address)
            p.save()
            if p.ip_addresses.count() % 10 == 0:
                user.profile.identity_verified = False
                user.profile.save()
            if user.security_profile.ip_addresses.count() > 1:
                messages.warning(request, 'You are using a new IP. Please verify your identity.')
                user.profile.identity_confirmed = False
                user.profile.save()
        p = user.profile
        ip_obj = user.security_profile.ip_addresses.filter(ip_address=ip).first()
        risk_detected = ip_obj.risk_detected
        if risk_detected or risk_detected == None:
            p.identity_verified = False
            p.identity_verification_failed = True
            p.save()
            messages.warning(request, 'You are using a suspicious IP. You have been logged out of the server.')
            logout(request)
            return HttpResponse(reverse('landing:landing'))
        ip_obj.page_loads = ip_obj.page_loads + 1
        if ip_obj.page_loads % FRAUD_MOD == 0:
            ip_obj.risk_detected = check_ip_risk(ip_obj)
        ip_obj.save()
        risk_detected = ip_obj.risk_detected
        if risk_detected or risk_detected == None:
            p.identity_verified = False
            p.identity_verification_failed = True
            p.save()
            messages.warning(request, 'You are using a suspicious IP. You have been logged out of the server.')
            logout(request)
            return HttpResponse(reverse('landing:landing'))
    next = request.GET.get('next','')
    if request.method == 'POST' and (user.profile.can_face_login < timezone.now() or not user) and not fraud_detect(request, True):
        form = FaceForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.warning(request, 'The form did not validate. Please try again.')
            return HttpResponse(status=200)
        form.instance.token = request.GET.get('token', 'none')
        face = form.save()
        from face.deep import is_face
        if is_face(face.image.path):
            from feed.align import face_rotation
            rot = face_rotation(face.image.path)
            if rot == -1:
                face.rotate_left()
            elif rot == 1:
                face.rotate_right()
#            face.rotate_align()
        result = False
        try:
            # prelim. result, token and timestamp
            result = True
            if user: result = user.profile.check_face_token(token) and user.profile.can_face_login < timezone.now()
            from face.face import is_face_user
            result = result and is_face_user(face.image.path, user)
        except:
            set_current_exception(traceback.format_exc())
            raise FaceLoginFailedException()
            print(traceback.format_exc())
            print('Face not recognized.')
        face.user = user
        face.save()
        if flow:
            flow.face = face
            flow.save()
        if result:
            qs = '?'
            for key, value in request.GET.items():
                qs = qs + key + '=' + value + '&'
            auth_url = None
            if user:
                auth_url = User.objects.get(id=user.id).profile.create_auth_url() + qs
            face.auth_url = auth_url if user and not request.GET.get('flow', False) else reverse('barcode:scan') + '?flow={}'.format(request.GET.get('flow'))
            face.session_key = request.session.session_key
            face.authentic = True
            face.save()
            # Delete old face photo
#            old_faces = Face.objects.filter(user=user).order_by('-timestamp')
#            if old_faces.count() > 32:
#                old_faces.last().delete()
            if user:
                user.profile.can_face_login = timezone.now()
                user.profile.save()
            messages.success(request, 'Your face has been accepted.')
            print(auth_url)
            return HttpResponse(face.auth_url)
        else:
            face.delete_photo()
            if user.profile.can_face_login > timezone.now():
                messages.warning(request, 'You can\'t log in with your face until after {}, sorry.'.format(user.profile.can_face_login.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%A %H:%M:%S")))
            if not user.profile.check_face_token(token):
                messages.warning(request, 'Your URL token for face login has expired. Please return to the login to create a new token.')
                return HttpResponse(reverse('users:login'))
            user.profile.can_face_login = timezone.now() + datetime.timedelta(seconds=5)
            user.profile.save()
            return HttpResponse(status=200)
    hide_logo = None
    if user.profile.hide_logo:
        hide_logo = True
    token = get_random_string(length=64)
    return render(request, 'face/face.html', {'dontshowsidebar': True, 'full': True, 'form': FaceForm(), 'title': 'Log in with your face', 'description': 'Log in to {} or create a new account with your face using a single tap.'.format(settings.SITE_NAME), 'hide_logo': hide_logo, 'profile': user.profile, 'accl_logout': user.profile.shake_to_logout, 'load_timeout': 3000, 'auth_token': token, 'user_uuid': user.profile.uuid})
