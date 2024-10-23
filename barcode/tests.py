from django.test import TestCase

# Create your tests here.
def document_scanned(user):
    from barcode.models import DocumentScan
    import datetime
    from django.utils import timezone
    from django.conf import settings
    return DocumentScan.objects.filter(user=user, verified=True, side=True, foreign=False, timestamp__gte=timezone.now() - datetime.timedelta(hours=settings.ID_VALID_HOURS)).count() and DocumentScan.objects.filter(user=user, verified=True, side=False, foreign=False, timestamp__gte=timezone.now() - datetime.timedelta(hours=settings.ID_VALID_HOURS)).count()
