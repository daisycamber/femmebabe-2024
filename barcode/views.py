from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from feed.tests import identity_verified
#from .validate import barcode_valid

@login_required
@csrf_exempt
def validate_barcode(request, key):
    from .models import DocumentScan
    from django.http import HttpResponse
    return HttpResponse('y' if DocumentScan.objects.filter(key=key).count() > 0 and DocumentScan.objects.filter(key=key).last().succeeded else 'n')

#@login_required
def scan_barcode(request):
    from verify.models import VeriFlow
    from django.urls import reverse
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.models import User
    from users.models import Profile
    #from lotteh.celery import face_id_task
    from django.contrib import messages
    from django import forms
    from django.http import HttpResponse, HttpResponseRedirect
    from django.core.files.uploadedfile import InMemoryUploadedFile
    import base64
    import io, os
    import base64, uuid
    from django.utils.crypto import get_random_string
    from django.contrib.auth import login
    from security.models import UserIpAddress
    from security.middleware import get_client_ip
    import traceback
    from security.models import UserIpAddress
    from django.contrib.auth import logout
    from security.middleware import FRAUD_MOD
    import datetime, pytz, uuid
    from datetime import date
    from django.utils import timezone
    from django.conf import settings
    from security.middleware import get_uuid
    from feed.middleware import set_current_exception
    from django.core.exceptions import PermissionDenied
    from security.security import fraud_detect
    import time
    from .forms import ScanForm
    from PIL import Image, ImageFile
    from face.deep import is_face
    from .scan import scan_id as scan_id_front
    from .blur_detection import detect_blur
    from security.middleware import get_qs
    from verify.idscan import decode_barcode
    from feed.templatetags.nts import number_to_string
    from .barcode import barcode_valid
    from .idscan import scan_id as scan_id_back
    from PIL import Image
    flow = None
    if request.GET.get('flow', False): flow = VeriFlow.objects.filter(uid=request.GET.get('flow', None), expires__gte=timezone.now()-datetime.timedelta(minutes=15))
    if not flow and not request.user.is_authenticated: return HttpResponseRedirect(reverse('users:login') + '?next=' + reverse('barcode:scan'))
    ip = get_client_ip(request)
    next = request.GET.get('next')
    back = False
    if request.GET.get('back', None):
        back = True
    foreign = False
    if request.GET.get('foreign', None):
        foreign = True
        if not (request.user.profile.admin or request.user.is_superuser or request.user.profile.idscan_active):
            foreign = False
            messages.warning(request, 'You need to buy an ID scanner plan before continuing.')
            return redirect(reverse('payments:idscan'))
    if flow: foregin = True
    if request.user.profile.idscan_active and not request.GET.get('auth', False): foreign = True
    if request.user.is_authenticated and not foreign and not request.user.faces.count():
        messages.warning(request, 'You need to take a photo of your face before scanning your ID.')
        return redirect(request.user.profile.create_face_url() + '?next=/barcode/')
    if request.user.is_authenticated and (not back and (request.user.profile.id_front_scanned and not request.user.profile.id_back_scanned and not foreign and not request.user.profile.idscan_active and not request.GET.get('download'))):
        return redirect(request.path + get_qs(request.GET) + '&back=true')
    if request.user.is_authenticated and ((request.user.profile.id_front_scanned and request.user.profile.id_back_scanned and not foreign and not request.user.profile.idscan_active and not request.GET.get('download'))):
        return redirect(request.GET.get('next') or '/')
    if request.method == 'POST' and not fraud_detect(request, True) and ((not request.user.is_authenticated) or (request.user.profile.idscan_used < request.user.profile.idscan_plan if request.user.profile.idscan_active else True)):
        if request.user.is_authenticated:
            request.user.profile.idscan_used = request.user.profile.idscan_used + 1
            request.user.profile.save()
        else:
            flow.user.profile.idscan_used = flow.user.profile.idscan_used + 1
            flow.user.profile.save()
        if request.user.is_authenticated and request.user.profile.can_scan_id > timezone.now():
            messages.warning(request, 'Please wait a few minutes before scanning another ID.')
            return redirect(reverse('barcode:scan') + get_qs(request.GET))
        form = ScanForm(request.POST, request.FILES)
        if not form.is_valid():
            messages.warning(request, 'The form did not validate. Please try again.')
            return HttpResponse(reverse('barcode:scan') + get_qs(request.GET))
        form.instance.user = request.user if request.user.is_authenticated else None
        scan = form.save()
        if flow:
            flow.scans.add(scan)
            flow.save()
        scan.side = not back
        scan.foreign = True if request.GET.get('foreign', None) else False
        scan = form.save()
        if detect_blur(scan.document.path):
            messages.warning(request, 'The scan was blurry. Please try again.')
            return HttpResponse(reverse('barcode:scan') + get_qs(request.GET))
        request.user.profile.save()
        is_valid = False
        birthday = None
        try:
            if back:
                try:
                    res = barcode_valid(scan)
                    if not res:
                        scan.rotate()
                        res = barcode_valid(scan)
                    birthday, expiry = res
                    if not birthday:
                        is_valid = False
                        messages.warning(request, 'Your ID was not accepted due to missing or invalid documentation.')
                        scan.succeeded = True
                        scan.save()
                        return HttpResponse(request.path + get_qs(request.GET))
                    else:
                        scan.birthday = birthday
                        if expiry:
                            scan.expiry = expiry
                        scan.save()
                        is_valid = True
                except:
                    print(traceback.format_exc())
                    messages.warning(request, 'This ID scan was not accepted. Please try again.')
                    scan.succeeded = True
                    scan.save()
                    return HttpResponse(request.path + get_qs(request.GET))
                try:
                    if settings.USE_IDWARE and not decode_barcode(scan.barcode_data, scan):
                        messages.warning(request, 'This ID did not validate with IDWare.')
                        is_valid = False
                except:
                    is_valid = False
                    print(traceback.format_exc())
                    messages.warning(request, 'There was an error with the IDWare API. The API quota was likely exceeded.')
                prev_scan = DocumentScan.objects.filter(idscan=scan.idscan).last()
                if prev_scan and prev_scan.user != scan.user and prev_scan.user and not foreign and not request.user.profile.idscan_active:
                    is_valid = False
                    messages.warning(request, 'A previous scan of this ID already exists under a different account.')
                prev_scan = DocumentScan.objects.filter(barcode_data=scan.barcode_data).last()
                if prev_scan and prev_scan.user != scan.user and prev_scan.user and not foreign and not request.user.profile.idscan_active:
                    is_valid = False
                    messages.warning(request, 'A previous scan of this ID already exists under a different account.')
            else:
                try:
                    res = scan_id_front(scan, foreign, lang=settings.OCR_LANG)
                    if not res:
                        res = scan_id_front(scan, foreign, lang=settings.OCR_LANG)
                    if not res:
                        res = scan_id_front(scan, foreign, lang=None)
                    if not res:
                        scan.rotate()
                        res = scan_id_front(scan, foreign, lang=settings.OCR_LANG)
                    if not res:
                        res = scan_id_front(scan, foreign, lang=None)
                    birthday, expiry = res
                    if not birthday:
                        print('Birthday not recognized.')
                        is_valid = False
                    else: is_valid = True
                except:
                    is_valid = False
        except:
            print(traceback.format_exc())
            is_valid = False
            messages.warning(request, 'The scan was unsuccessful. Please try again.')
#        if back:
#            request.user.profile.can_scan_id = timezone.now() + datetime.timedelta(minutes=settings.MINUTES_PER_IDSCAN)
#            if request.user.profile.vendor or request.user.is_superuser or request.user.profile.idscan_active:
#                request.user.profile.can_scan_id = timezone.now() + datetime.timedelta(minutes=settings.MINUTES_PER_IDSCAN_STAFF)
        scan.save()
        if is_valid:
            scan.succeeded = True
            scan.save()
            today = date.today()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            messages.success(request, 'This ID has been accepted. Age {} ({}) years old.'.format(number_to_string(age), str(age)) + (' Please upload a scan of the back too.') if not back else '')
            if back:
                if request.user.is_authenticated and not foreign:
                    request.user.profile.id_back_scanned = True
                    request.user.profile.save()
                scan.verified = True
                scan.save()
                if request.user.is_authenticated and not foreign and not request.user.profile.idscan_active:
                    return HttpResponse(reverse('survey:answer') + ('?next=' + next) if next else '')
                elif flow:
                    return HttpResponse(flow.next)
                else:
                    return HttpResponse(reverse('barcode:scan') + get_qs(request.GET))
            else:
                if request.user.is_authenticated and not foreign and not request.user.profile.idscan_active:
                    request.user.profile.id_front_scanned = True
                    request.user.profile.save()
                scan.verified = True
                scan.save()
                return HttpResponse(reverse('barcode:scan') + get_qs(request.GET) + '&back=true')
        else:
            messages.warning(request, 'Your ID was not accepted. Please try again.')
            if not foreign:
                if back:
                    request.user.profile.id_back_scanned = False
                    request.user.profile.save()
                else:
                    request.user.profile.id_front_scanned = False
                    request.user.profile.save()
            return HttpResponse(reverse('barcode:scan') + get_qs(request.GET) + ('&back=true') if back else '')
    key = str(uuid.uuid4())
    return render(request, 'barcode/scan.html', {'dontshowsidebar': True, 'full': True, 'form': ScanForm(initial={'key': key}), 'title': 'Scan {} ID {}'.format('the' if foreign else 'your', 'back' if back else 'front'), 'back': back, 'preload': True, 'load_timeout': 3000, 'key': key, 'securitymodal': False, 'securitymodaljs': False})
