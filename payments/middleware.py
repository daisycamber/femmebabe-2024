from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
import traceback
from django.http import HttpResponse, HttpResponseRedirect
import uuid
from stacktrace.models import Error
from django.utils import timezone
from payments.models import Subscription
from security.apis import get_client_ip
from django.http import HttpResponseRedirect
from django.conf import settings

# Static IPS and ID for paymentcloud
moderator_ips = None # []
moderator_id = settings.MODERATOR_USER_ID

def payments_middleware(get_response):
    # One-time configuration and initialization.
    def middleware(request):
        response = None
        try:
            response = get_response(request)
        except:
            print(traceback.format_exc())
        return response
    return middleware
