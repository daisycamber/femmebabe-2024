from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from users.models import Profile
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
from vendors.tests import is_vendor
from django.core.exceptions import PermissionDenied
from django.http import StreamingHttpResponse
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import uuid
import imghdr
import os
from .models import Camera
from .forms import CameraForm
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile

folder = 'live/'

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
@csrf_exempt
def golive(request):
    cameras = Camera.objects.filter(user=request.user)
    camera = None
    if cameras.count() == 0:
        camera = Camera.objects.create(user=request.user)
        camera.save()
    else:
        camera = cameras.first()
    if request.method == 'POST':
        print(request.FILES)
        form = CameraForm(request.POST, request.FILES, instance=camera)
        if form.is_valid():
            form.save()
        print("Working")
        return redirect('live:live')
    return render(request, 'live/golive.html', {'object': request.user.camera, 'form': CameraForm()})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def live(request, username):
    profile = get_object_or_404(Profile, user__username=username, identity_verified=True, vendor=True)
    cameras = Camera.objects.filter(user=profile.user)
    return render(request, 'live/live.html', {'profile': profile, 'camera': cameras.first()})


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def frame(request, username):
    profile = get_object_or_404(Profile, user__username=username, identity_verified=True, vendor=True)
    return render(request, 'live/live_frame.html', {'profile': profile})
