from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from django.contrib.sessions.models import Session
from security.views import all_unexpired_sessions_for_user
from django.contrib.auth.models import User

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
#@user_passes_test(is_vendor)
def hypnosis(request):
    return render(request, 'hypnosis/hypnosis.html', {'title': 'Hypnosis', 'hidenavbar': True})
