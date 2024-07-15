from django.test import TestCase
from datetime import timedelta
from django.utils import timezone

def melanin_valid(user):
    from .models import MelaninPhoto
    return MelaninPhoto.objects.filter(user=user, timestamp__gt=timezone.now() - timedelta(minutes=settings.MELANIN_VERIFICATION_MINUTES)).count() > 0
