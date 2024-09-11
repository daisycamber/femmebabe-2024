from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from vendors.models import VendorProfile
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified, identity_really_verified
from .forms import VendorProfileUpdateForm
from django.utils import timezone
import pytz

def pornhub(request, username):
    from .models import VendorProfile
    from django.shortcuts import redirect
    from django.contrib import messages
    from security.apis import get_client_ip, check_raw_ip_risk
    if not request.COOKIES.get('age_verified', None) or check_raw_ip_risk(get_client_ip(request), True, False):
        messages.warning(request, 'You may not visit this link, as per the site policies.')
        return redirect(reverse('/'))
    profile = VendorProfile.objects.filter(user__profile__name=username).first()
    return redirect('/' if not profile.pornhub_link else profile.pornhub_link)

def onlyfans(request, username):
    from .models import VendorProfile
    from django.shortcuts import redirect
    from django.contrib import messages
    from security.apis import get_client_ip, check_raw_ip_risk
    if not request.COOKIES.get('age_verified', None) or check_raw_ip_risk(get_client_ip(request), True, False):
        messages.warning(request, 'You may not visit this link, as per the site policies.')
        return redirect(reverse('/'))
    profile = VendorProfile.objects.filter(user__profile__name=username).first()
    return redirect('/' if not profile.onlyfans_link else profile.onlyfans_link)

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def send_bitcoin(request):
    from .models import VendorPaymentsProfile
    from django.shortcuts import render
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=request.user)
    return render(request, 'vendors/send_bitcoin.html', {'title': 'Crypto', 'info': profile.get_crypto_balances()})


@login_required
@user_passes_test(identity_really_verified, login_url='/verify/', redirect_field_name='next')
def onboarding(request):
    from django.shortcuts import redirect
    from django.urls import reverse
    from payments.models import VendorProfile
    if not hasattr(request.user, 'vendor_profile'):
        v = VendorProfile.objects.create(user=request.user)
        v.save()
        request.user.profile.vendor = True
        request.user.profile.save()
    return redirect(reverse('feed:profile', kwargs={'username': request.user.username}))

@login_required
@user_passes_test(identity_really_verified, login_url='/verify/', redirect_field_name='next')
def vendor_preferences(request):
    from django.shortcuts import redirect, render
    from django.urls import reverse
    from payments.models import VendorPaymentsProfile
    from .forms import VendorProfileUpdateForm
    from django.contrib import messages
    v, created = VendorProfile.objects.get_or_create(user=request.user)
    v.save()
    form = VendorProfileUpdateForm(instance=v)
    if request.method == 'POST':
        form = VendorProfileUpdateForm(request.POST, instance=request.user.vendor_profile)
        if form.is_valid():
            form.instance.user = request.user
            p = form.save()
            p.user.profile.vendor = True
            p.user.profile.save()
            messages.success(request, 'Vendor profile updated.')
            return redirect(reverse('go:go'))
    return render(request, 'vendors/vendor_preferences.html', {'title': 'Vendor Preferences','form': form})
