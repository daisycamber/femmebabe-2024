from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def notes(request):
    from .models import BirthControlPill
    from django.http import HttpResponse
    if request.method == 'POST':
        last_pill = BirthControlPill.objects.filter(patient=request.user).last()
        v = ''
        for key, value in request.POST.items():
            v = v + key + value
        if last_pill:
            last_pill.notes_save = v
            last_pill.save()
    return HttpResponse(status=200)

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def temperature(request):
    from django.core.paginator import Paginator
    from django.shortcuts import render
    from .forms import BirthControlForm, BirthControlProfileForm, BirthControlTimeForm
    from .models import BirthControlPill, BirthControlProfile
    from django.utils import timezone
    import datetime
    from django.contrib import messages
    from django.http import HttpResponse
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    pills = True
    x = 0
    months = []
    while pills:
        pills = BirthControlPill.objects.filter(patient=request.user, time_taken__gte=timezone.now().replace(day=1, hour=0, minute=0) - datetime.timedelta(days=31 * x), time_taken__lte=timezone.now().replace(day=1) + datetime.timedelta(days=31) - datetime.timedelta(days=31 * x)).order_by('-time_taken')
        months = months + [[pills]]
        x = x + 1
    p = Paginator(months, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'birthcontrol/temperature.html', {
        'title': 'Temperature Charting',
        'months': p.page(page),
        'count': p.count,
        'page_obj': p.get_page(page),
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def profile(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from .forms import BirthControlForm, BirthControlProfileForm, BirthControlTimeForm
    from .models import BirthControlPill, BirthControlProfile
    from django.utils import timezone
    import datetime
    from django.contrib import messages
    import pytz
    from django.http import HttpResponse
    from django.conf import settings
    from .barcode import decode_barcodes
    from .isolate import decode_isolated
    profile, created = BirthControlProfile.objects.get_or_create(patient=request.user)
    if request.method == 'POST':
        form = BirthControlProfileForm(request.POST, request.FILES, instance=profile)
        if request.FILES:
            form.instance.birth_control_uploaded = timezone.now()
        errors = ''
        if form.is_valid():
            try:
                form.instance.reminder_time = datetime.datetime.combine(timezone.now().date(), datetime.datetime.strptime(form.data.get('reminder_time'), "%H:%M:%S").time())
            except:
                try:
                    form.instance.reminder_time = datetime.datetime.combine(timezone.now().date(), datetime.datetime.strptime(form.data.get('reminder_time'), "%H:%M").time())
                except: form.instance.reminder_time = timezone.now()
            profile = form.save()
            messages.success(request, 'Profile saved!')
            if request.FILES:
                import zxing
                reader = zxing.BarCodeReader()
                barcode = str(reader.decode(profile.birth_control.path))
                profile.birth_control_barcodes = barcode #decode_isolated(profile.birth_control.path)
                profile.save()
        else:
            messages.warning(request, str(form.errors))
    return render(request, 'birthcontrol/profile.html', {'form': BirthControlProfileForm(instance=profile, initial={'reminder_time': profile.reminder_time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%H:%M:00")})})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def take_birth_control_time(request):
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from .forms import BirthControlForm, BirthControlProfileForm, BirthControlTimeForm
    from .models import BirthControlPill, BirthControlProfile
    from django.utils import timezone
    import datetime
    from django.contrib import messages
    import pytz
    from django.conf import settings
    last_pill = BirthControlPill.objects.filter(patient=request.user).last()
    pills = BirthControlPill.objects.filter(patient=request.user)
    seclast_pill = None
    if pills.count() > 1:
        seclast_pill = pills[pills.count() - 2]
    if request.method == 'POST':
        form = BirthControlTimeForm(request.POST)
        if form.is_valid():
            try:
                last_pill.time_taken = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M:%S.%f').time())
            except:
                try:
                    last_pill.time_taken = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M:%S').time())
                except:
                    try:
                        last_pill.time_taken = datetime.datetime.combine(datetime.datetime.strptime(form.data.get('date'), '%Y-%m-%d').date(), datetime.datetime.strptime(form.data.get('time'), '%H:%M').time())
                    except: last_pill.time_taken = timezone.now()
            last_pill.save()
            messages.success(request, 'The time was saved.')
            return redirect(reverse('go:go'))
    return render(request, 'birthcontrol/take_time.html', {
        'title': 'Edit BC time',
        'form': BirthControlTimeForm(initial={'date': ((seclast_pill if seclast_pill else last_pill).time_taken.astimezone(pytz.timezone(settings.TIME_ZONE)) + datetime.timedelta(hours=24)).strftime("%Y-%m-%d"), 'time': (seclast_pill if seclast_pill else last_pill).time_taken.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%H:%M:00")}),
        'last_pill': last_pill,
        'current_time': timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%a %b %d %Y %H:%M:%S GMT-0700 (Pacific Daylight Time)')
    })

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def take_birth_control(request):
    from django.core.paginator import Paginator
    from django.shortcuts import render
    from django.shortcuts import redirect
    from django.urls import reverse
    from .forms import BirthControlForm, BirthControlProfileForm, BirthControlTimeForm
    from .models import BirthControlPill, BirthControlProfile
    from django.utils import timezone
    import datetime
    from django.contrib import messages
    import pytz
    from django.http import HttpResponse
    from django.conf import settings
    last_pill = BirthControlPill.objects.filter(patient=request.user).last()
    profile, created = BirthControlProfile.objects.get_or_create(patient=request.user)
    if request.method == 'POST':
        form = BirthControlForm(request.POST)
        if form.is_valid():
            if not form.data.get('taken_now'):
                form = BirthControlForm(request.POST, instance=last_pill)
                if not form.is_valid(): print('Invalid form with instance')
            form.instance.patient = request.user
            extra = ''
            if form.instance.notes:
                extra = ' Nice note!'
            if last_pill and last_pill.time_taken + datetime.timedelta(minutes=1435) < timezone.now() or not form.data.get('taken_now', False):
                if last_pill:
                    last_pill.notes_save = ''
                    form.instance.reminders = profile.reminders
                    form.instance.patient.birthcontrol_profile
                    profile.reminders = 0
                    profile.save()
                    last_pill.save()
                if form.data.get('taken_now'):
                    form.instance.time_taken = last_pill.time_taken + datetime.timedelta(hours=24)
                    form.save()
                    messages.success(request, 'You took your birth control.' + extra + ' Please supply a time if different from the last.')
                    return redirect(reverse('birthcontrol:take-time'))
                form.save()
                messages.success(request, 'You took your birth control.' + extra)
            elif not last_pill:
                messages.success(request, 'You took your birth control.' + extra + ' This is your first pill.')
                form.save()
            else:
                last_pill.notes_save = form.instance.notes
                last_pill.save()
                messages.warning(request, 'You can\'t take your birth control until ' + (last_pill.time_taken + datetime.timedelta(minutes=1440)).astimezone(pytz.timezone('US/Pacific')).strftime("%H:%M:%S"))
    pills = BirthControlPill.objects.filter(patient=request.user).order_by('-time_taken')
    page = 1
    if(request.GET.get('page', '') != ''):
        page = int(request.GET.get('page', ''))
    p = Paginator(pills, 10)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    init = ''
    if last_pill:
        init = last_pill.notes_save
    form = BirthControlForm(initial={'notes':init})
    if not last_pill: last_pill = {'id': 0, 'short_time': '09:00:00'}
    return render(request, 'birthcontrol/take.html', {'title': 'Take a Birth Control Pill', 'form': form, 'pills': p.page(page), 'count': p.count, 'page_obj': p.get_page(page), 'last_pill': last_pill,
        'the_current_time': timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%a %b %d %Y %H:%M:%S GMT-0700 (Pacific Daylight Time)')
    })
