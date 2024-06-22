from .models import IDScanSubscription
import stripe
from django.contrib.auth.models import User

def update_privledges():
    for user in User.objects.all():
        if not user.payment_links.objects.filter(valid=False): continue
        for payment_link in user.payment_links.objects.filter(valid=False):
            
