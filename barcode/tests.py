from django.test import TestCase

# Create your tests here.
def document_scanned(user):
    from barcode.models import DocumentScan
    return DocumentScan.objects.filter(user=user, verified=True, side=True, foreign=False).count() and DocumentScan.objects.filter(user=user, verified=True, side=False, foreign=False).count()