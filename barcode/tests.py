from django.test import TestCase

# Create your tests here.
def document_scanned(user):
    return DocumentScan.objects.filter(user=request.user, verified=True, side=True, foregin=False).count() and DocumentScan.objects.filter(user=request.user, verified=True, side=False, foreign=False).count()
