from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def is_kick(ip, user):
    from security.models import UserIpAddress
    ips = []
    ips = UserIpAddress.objects.filter(ip_address=ip)
    if user and user.is_authenticated:
        ips = UserIpAddress.objects.filter(ip_address=ip, user=user)
    k = False
    for i in ips: # i.user
        if (i.risk_detected and not i.risk_recheck) or (i.user and (i.user.profile.kick or not i.user.is_active)):
            return True
    return False

def reasess_kick(request):
    from django.shortcuts import redirect
    from django.http import HttpResponse
    from django.contrib.auth import logout
    from security.apis import check_ip_risk, get_client_ip
    from django.urls import reverse
    from django.contrib import messages
    from .forms import AppealForm
    from security.models import UserIpAddress
    from feed.templatetags.nts import number_to_string
    if request.method == 'POST':
        form = AppealForm(request.POST)
        if form.is_valid():
            ip = get_client_ip(request)
            uips = UserIpAddress.objects.filter(ip_address=ip, risk_detected=True)
            if uips.count() > 0:
                for ip_addr in uips:
                    ip_addr.risk_detected = check_ip_risk(ip_addr)
                    ip_addr.save()
                messages.success(request, 'Your request has been accepted. We have updated {} ips.'.format(number_to_string(uips.count())))
                return redirect(reverse('users:login'))
            else:
                messages.warning(request, 'Your IP address is not in our records.')
    from django.shortcuts import render
    return render(request, 'kick/reasess.html', {'title': 'Reasess Kick', 'form': AppealForm()})

@csrf_exempt
def should_kick(request):
    from django.http import HttpResponse
    from django.contrib.auth import logout
    from security.apis import check_ip_risk, get_client_ip
    if request.user.is_authenticated and not request.user.profile.kick:
        return HttpResponse('n')
    ip = get_client_ip(request)
    from security.security import fraud_detect
    if is_kick(ip, request.user) or request.GET.get('hard') and fraud_detect(request):
        logout(request)
        return HttpResponse('y')
    return HttpResponse('n')
