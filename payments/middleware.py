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
            if request.user.is_authenticated:
                if moderator_ips and request.user.id == moderator_id and not get_client_ip(request) in moderator_ips:
                    messages.warning(request, 'Please do not attempt to access the moderator account without a static IP supplied to me. You have been logged out.')
                    logout(request)
                    return HttpResponseRedirect(reverse('landing:landing'))
                if Subscription.objects.filter(user=request.user).count() > 0:
                    user = request.user
                    for sub in Subscription.objects.filter(user=request.user):
                        if sub.expire_date < timezone.now():
                            user.subscriptions.remove(sub.model)
                            user.save()
                            sub.delete()
            response = get_response(request)
        except:
            print(traceback.format_exc())
        return response
    return middleware
