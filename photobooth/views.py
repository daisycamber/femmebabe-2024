from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def photo(request, camera):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from django.contrib import messages
    from django.contrib.auth.models import User
    from feed.forms import PostForm
    from django.http import HttpResponse
    from .models import Camera
    from .forms import RemoteForm
    from datetime import timedelta
    from django.conf import settings
    payload = {
        'head': 'Tap to take a photo on {}'.format(settings.SITE_NAME),
        'body': 'Open this notification and you will take a photo on your camera connected to {}'.format(settings.SITE_NAME),
        'icon': settings.BASE_URL + settings.ICON_URL,
        'url': settings.BASE_URL + request.path +"?time=" + request.GET.get('time', '5'),
    }
    from pwa_webpush import send_user_notification
    try:
        send_user_notification(request.user, payload=payload)
    except: pass
    if request.GET.get('init', None):
        return render(request, 'close.html')
    camera, created = Camera.objects.get_or_create(name=camera, user=request.user)
    camera.connected = timezone.now()
    camera.data = request.GET.get('time', '5')
    camera.save()
    return render(request, 'close.html')

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def photobooth(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from django.contrib import messages
    from django.contrib.auth.models import User
    from feed.forms import PostForm
    from django.http import HttpResponse
    from .models import Camera
    from .forms import RemoteForm
    from datetime import timedelta
    from django.conf import settings
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.private = True
            form.instance.author = request.user
            form.instance.content = request.GET.get('content', '')
            if request.GET.get('recipient') and User.objects.filter(profile__name=request.GET.get('recipient')).first():
                form.instance.recipient = User.objects.get(profile__name=request.GET.get('recipient'))
            post = form.save()
            print('You have saved this photo.')
            return HttpResponse(200)
    return render(request, 'photobooth/photobooth.html', {'title': 'Photo Booth', 'form': PostForm(), 'profile': request.user.profile, 'preload': True, 'start_time': timezone.now().strftime("%m%d%Y-%H%M%S")})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def remote(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.sessions.models import Session
    from django.contrib import messages
    from django.contrib.auth.models import User
    from feed.forms import PostForm
    from django.http import HttpResponse
    from .models import Camera
    from .forms import RemoteForm
    from datetime import timedelta
    from django.conf import settings
    return render(request, 'photobooth/remote.html', {'title': 'Photo Remote', 'form': RemoteForm(), 'profile': request.user.profile, 'preload': True, 'cameras': Camera.objects.filter(connected__gte=timezone.now() - timedelta(hours=24))})
