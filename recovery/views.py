from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified

def get_password_reset_url(self):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from security.views import all_unexpired_sessions_for_user
    from django.contrib.auth.models import User
    from face.forms import FaceForm
    from security.security import fraud_detect
    from verify.models import IdentityDocument
    from .forms import RecoveryForm
    from django.utils.crypto import get_random_string
    from django.http import HttpResponse
    from django.contrib import messages
    from barcode.models import DocumentScan
    from django import utils
    from django.conf import settings
    from django.contrib.auth.tokens import PasswordResetTokenGenerator
    from django.urls import reverse
    base64_encoded_id = utils.http.urlsafe_base64_encode(utils.encoding.force_bytes(self.id))
    token = PasswordResetTokenGenerator().make_token(self)
    reset_url_args = {'uidb64': base64_encoded_id, 'token': token}
    reset_path = reverse('password_reset_confirm', kwargs=reset_url_args)
    reset_url = f'{settings.BASE_URL}{reset_path}'
    return reset_url

def recover(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from security.views import all_unexpired_sessions_for_user
    from django.contrib.auth.models import User
    from face.forms import FaceForm
    from security.security import fraud_detect
    from verify.models import IdentityDocument
    from .forms import RecoveryForm
    from django.utils.crypto import get_random_string
    from django.http import HttpResponse
    from django.contrib import messages
    from barcode.models import DocumentScan
    from django import utils
    from django.conf import settings
    from django.contrib.auth.tokens import PasswordResetTokenGenerator
    from django.urls import reverse
    if request.method == 'POST':
        form = RecoveryForm(request.POST)
        if form.is_valid():
            return redirect(reverse('recovery:recovery', kwargs={'name': form.data.get('your_name')}))
    return render(request, 'recovery/recover.html', {'title': 'Recover your account', 'form': RecoveryForm()})

def recovery(request, name):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from security.views import all_unexpired_sessions_for_user
    from django.contrib.auth.models import User
    from face.forms import FaceForm
    from security.security import fraud_detect
    from verify.models import IdentityDocument
    from .forms import RecoveryForm
    from django.utils.crypto import get_random_string
    from django.http import HttpResponse
    from django.contrib import messages
    from barcode.models import DocumentScan
    from django import utils
    from django.conf import settings
    from django.contrib.auth.tokens import PasswordResetTokenGenerator
    from django.urls import reverse
    users = User.objects.filter(username=name)
    users = users.union(User.objects.filter(profile__name=name))
    users = users.union(User.objects.filter(profile__preferred_name=name))
    user = users.first()
    if request.method == 'POST':
        form = FaceForm(request.POST, request.FILES)
        if form.is_valid():
            face = form.save()
            from face.face import is_face_user
            if is_face_user(face.image.path, user) and user.faces.count() > 0:
                user.profile.recovery_token = get_random_string(length=16)
                user.profile.save()
                face.user = user
                face.save()
                messages.success(request, 'Your face has been accepted.')
                return HttpResponse(reverse('recovery:secure', kwargs={'token': user.profile.recovery_token}))
            else:
                messages.warning(request, 'Your face was not accepted.')
    return render(request, 'face/face.html', {'title': 'Recover your ID', 'form': FaceForm(), 'full': True, 'profile': user.profile})

def user_recovery(request, token):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from security.views import all_unexpired_sessions_for_user
    from django.contrib.auth.models import User
    from face.forms import FaceForm
    from security.security import fraud_detect
    from verify.models import IdentityDocument
    from .forms import RecoveryForm
    from django.utils.crypto import get_random_string
    from django.http import HttpResponse
    from django.contrib import messages
    from barcode.models import DocumentScan
    from django import utils
    from django.conf import settings
    from django.contrib.auth.tokens import PasswordResetTokenGenerator
    from django.urls import reverse
    if len(token) < 16:
        return redirect(reverse('recovery:recover'))
    user = User.objects.filter(profile__recovery_token=token).first()
    if not user:
        return redirect(reverse('recovery:recover'))
    front = DocumentScan.objects.filter(user=user, side=True).last()
    back = DocumentScan.objects.filter(user=user, side=False).last()
    return render(request, 'recovery/recovery.html', {
        'title': 'Your Information Recovered',
        'document': user.verifications.filter(verified=True).last(),
        'front': front,
        'back': back,
        'reset_url': get_password_reset_url(user),
    })
