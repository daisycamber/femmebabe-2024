from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import traceback
from django.http import HttpResponse, HttpResponseRedirect
import uuid
from stacktrace.models import Error
from django.utils import timezone
from payments.models import Subscription
from security.apis import get_client_ip
from django.http import HttpResponseRedirect
from barcode.models import DocumentScan
from verify.models import IdentityDocument

def barcode_middleware(get_response):
    def middleware(request):
        response = None
        try:
#            if request.user.is_authenticated:
#                if (DocumentScan.objects.filter(user=request.user, verified=True, side=True).count() == 0 or DocumentScan.objects.filter(user=request.user, verified=True, side=False).count() == 0) and (request.user.profile.id_back_scanned or request.user.profile.id_front_scanned) and not request.user.id == settings.MODERATOR_USER_ID: # comment last and not
#                    request.user.profile.id_front_scanned = False
#                    request.user.profile.id_back_scanned = False
#                    request.user.profile.save()
#                if IdentityDocument.objects.filter(user=request.user, verified=True).count() == 0 and request.user.profile.identity_verified and not request.user.id == settings.MODERATOR_USER_ID: # comment last and not
#                    request.user.profile.identity_verified = False
#                    request.user.profile.save()
            response = get_response(request)
        except:
            print(traceback.format_exc())
            response = get_response(request)
        return response
    return middleware
