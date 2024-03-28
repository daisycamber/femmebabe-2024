from django.shortcuts import render, redirect, get_object_or_404
from security.models import Session
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import InjectionForm
from django.core.paginator import Paginator
from face.tests import is_superuser_or_vendor

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def sessions(request):
    page = 1
    if(request.GET.get('page', None) != None):
        page = int(request.GET.get('page', 1))
    sessions = Session.objects.filter(index=2, method='GET', time__gte=timezone.now() - datetime.timedelta(minutes=60*24)).exclude(uuid_key='').order_by('-time')
    p = Paginator(sessions, 30)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'remote/sessions.html', {'title': 'Remote sessions', 'sessions': p.page(page), 'page_obj': p.get_page(page), 'count': p.count})

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def injection(request):
    past_injections = I
    sessions = Session.objects.filter(injection_key=request.GET.get('key', None), method='GET')
    if request.method == 'POST':
        form = InjectionForm(request.POST)
        if form.is_valid():
            for session in sessions:
                session.injection = form.cleaned_data.get('injection')
                session.injected = False
                session.save()
            messages.success(request, 'Injected into {} sessions.'.format(sessions.count()))
            return redirect(reverse('remote:sessions'))
        else: messages.warning(request, form.errors)
    return render(request, 'remote/injection.html', {'title': 'Inject JavaScript into Session', 'session': sessions.first(), 'form': InjectionForm(), 'past_injections': Session.objects.filter(time__gte=timezone.now()-datetime.timedelta(hours=24*120)).exclude(injected=False, injection='')})
