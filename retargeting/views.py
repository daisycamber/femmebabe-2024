from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from face.tests import is_superuser_or_vendor

def qrcode(request):
    from django.shortcuts import render
    return render(request, 'retargeting/qrcode.html', {'title': 'QR Code', 'description': 'Generate a QR code'})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def emails(request):
    from django.shortcuts import render
    from django.utils import timezone
    from .models import ScheduledEmail
    sent = request.GET.get('sent', False)
    emails = ScheduledEmail.objects.filter(sender=request.user, sent=False, send_at__gte=timezone.now()).order_by('-send_at') if not sent else ScheduledEmail.objects.filter(sender=request.user, sent=True, send_at__lte=timezone.now()).order_by('-send_at')
    return render(request, 'retargeting/emails.html', {'title': 'Scheduled Emails', 'emails': emails})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def send_email(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from django.utils import timezone
    from django.contrib.auth.models import User
    from feed.models import Post
    from django.conf import settings
    import datetime, pytz
    from .forms import EmailForm
    from .models import ScheduledEmail
    from django.contrib import messages
    id = request.GET.get('id', None)
    email = None
    if id: email = ScheduledEmail.objects.filter(id=int(id)).first()
    if request.method == 'POST' and request.user.profile.can_like < timezone.now() - datetime.timedelta(seconds=2) and (not email or not email.sent):
        form = EmailForm(request.POST, instance=email)
        if form.is_valid():
            email = form.save()
            try:
                email.send_at = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M:%S.%f').time())
            except:
                try:
                    email.send_at = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M:%S').time())
                except:
                    try:
                        email.send_at = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M').time())
                    except: email.send_at = timezone.now()
            email.recipient = request.GET.get('u', '') if request.GET.get('u', None) else ''
            email.sender = request.user
            email.save()
            messages.success(request, 'This email has been scheduled.')
            request.user.profile.can_like = timezone.now()
            request.user.profile.save()
        else: messages.warning(request, str(form.errors))
    send_at = timezone.now() + datetime.timedelta(minutes=60 * 3) if not request.GET.get('u', False) else timezone.now()
    form = EmailForm(instance=email, initial={'time': send_at.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:00'), 'date': send_at.astimezone(pytz.timezone(settings.TIME_ZONE)).date})
    return render(request, 'retargeting/send_email.html', {'title': 'Send Email', 'form': form, 'full': True})
