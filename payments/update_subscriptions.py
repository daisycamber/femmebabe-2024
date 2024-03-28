from django.urls import reverse
import traceback
from django.http import HttpResponse, HttpResponseRedirect
import uuid
from stacktrace.models import Error
from django.utils import timezone
from payments.models import Subscription
from django.contrib.auth.models import User
from payments.authorizenet import pay_fee
from datetime import datetime
from payments.models import PaymentCard

def update():
    for user in User.objects.all():
        if Subscription.objects.filter(user=user).count() > 0:
            for sub in Subscription.objects.filter(user=user):
                if sub.expire_date < timezone.now() and not sub.active:
                    user.subscriptions.remove(sub.model)
                    user.save()
                    sub.delete()
                elif sub.expire_date < timezone.now():
                    for card in PaymentCard.objects.filter(user=sub.user, primary=True):
                        if pay_fee(sub.model, sub.fee, card, name='Subscription to {}\'s profile'.format(user.profile.name), description='Recurring subscription for adult webcam modeling content.'):
                            sub.expire_date = timezone.now() + datetime.timedelta(hours=24*30)
                            sub.save()
                            break
                        else:
                            sub.active = False
                            sub.save()
                            user.subscriptions.remove(sub.model)
                            user.save()
                            card.delete()
