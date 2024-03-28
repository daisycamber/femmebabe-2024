from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from vendors.tests import is_vendor
from feed.tests import identity_verified, identity_really_verified
from django.contrib.auth.decorators import user_passes_test
from .models import Vibrator
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from barcode.tests import document_scanned
from django.conf import settings

# Create your views here.

@login_required
@user_passes_test(document_scanned, login_url='/barcode/', redirect_field_name='next')
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def vibe(request):
    return render(request, 'vibe/vibe.html', {'title': 'Vibrator Remote', 'full': True})

@csrf_exempt
@login_required
@user_passes_test(document_scanned, login_url='/barcode/', redirect_field_name='next')
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def remote_vibe(request):
    if not request.user.subscriptions.count():
        messages.warning(request, 'You need to subscribe to access this setting.')
        return redirect(reverse('feed:follow', kwargs={'username': User.objects.get(id=settings.MY_ID).profile.name}))
    vibrator, created = Vibrator.objects.get_or_create(user=request.user) # Write to the users vibrator
    if request.method == 'POST':
        data = ''
        for key, value in request.POST.items():
            data = data + key + value
        vibrator.setting = data
        vibrator.save()
    return render(request, 'vibe/remote_vibe.html', {'title': 'Vibrator Remote', 'full': True})

@login_required
@user_passes_test(document_scanned, login_url='/barcode/', redirect_field_name='next')
@user_passes_test(identity_really_verified, login_url='/verify/', redirect_field_name='next')
def receive_vibe(request, username):
    return render(request, 'vibe/receive_vibe.html', {'username': username, 'title': 'Vibrator Receiver', 'full': True})

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(identity_really_verified, login_url='/verify/', redirect_field_name='next')
def recieve_vibe_setting(request, username):
    vibrator, created = Vibrator.objects.get_or_create(user__profile__name=username)
    return HttpResponse(vibrator.setting)
