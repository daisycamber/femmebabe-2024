from django.test import TestCase
from django.contrib import messages
from feed.middleware import get_current_request
from payments.models import IDScanSubscription

def has_scan_privledge(user):
    return user.idware_privledge.objects.last() and user.idware_privledge.objects.last().active

# Create your tests here.
def identity_verified(user):
    return True
    if not user.profile.identity_verified:
        messages.warning(get_current_request(), 'You need to verify your identity before you may see this page.')
        return False
    return True

def identity_really_verified(user):
    if not user.profile.identity_verified:
        messages.warning(get_current_request(), 'You need to verify your identity before you may see this page.')
        return False
    return True
