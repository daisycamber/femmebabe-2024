from simple_history.models import HistoricalRecords
from django.db import models
from django.contrib.auth.models import User
import uuid, os, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.conf import settings
from jsignature.fields import JSignatureField
from feed.middleware import get_current_user
from address.models import AddressField

def get_document_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}-{}-{}'.format(uuid.uuid4(), instance.submitted.strftime("%Y%m%d-%H%M%S"), get_current_user().id if get_current_user() else 0), ext)
    return os.path.join('documents/', filename)

def get_signature_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('signature/', filename)

def get_past_date():
    return datetime.datetime.now() - relativedelta(years=settings.MIN_AGE)

def get_past_day():
    return datetime.datetime.now() - relativedelta(years=settings.MIN_AGE)

from barcode.models import DocumentScan
from face.models import Face

class VeriFlow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='veriflows')
    uid = models.CharField(default=uuid.uuid4, max_length=100)
    face = models.ForeignKey(Face, on_delete=models.DO_NOTHING, null=True, blank=True)
    scans = models.ManyToManyField(DocumentScan)
    next = models.CharField(default=uuid.uuid4, max_length=300, null=True, blank=True)

    def is_valid(self):
        return self.face.authorized and self.scans.filter(side=True, succeeded=True).count() > 0 and self.scans.filter(side=False, succeeded=True).count() > 0

class IdentityDocument(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='verifications')
    full_name = models.CharField(default='', max_length=100)
    address = AddressField(null=True, blank=True)
    document = models.ImageField(upload_to=get_document_path, null=True)
    document_isolated = models.ImageField(upload_to=get_document_path, null=True)
    document_back = models.ImageField(upload_to=get_document_path, null=True)
    document_back_isolated = models.ImageField(upload_to=get_document_path, null=True)
    signature = JSignatureField(null=True)
    document_number = models.TextField(default='', null=True, blank=True)
    document_ocr = models.TextField(default='', null=True, blank=True)
    barcode_data = models.TextField(default='', null=True, blank=True)
    barcode_data_processed = models.TextField(default='', null=True, blank=True)
    idscan = models.TextField(default='', null=True, blank=True)
    idscan_text = models.TextField(default='', null=True, blank=True)
    birthday = models.DateTimeField(default=timezone.now)
    submitted = models.DateTimeField(default=timezone.now)
    birthdate = models.DateTimeField(default=timezone.now)
    expiry = models.DateTimeField(default=timezone.now)
    expire_date = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        this = IdentityDocument.objects.filter(id=self.id).first()
        if this and this.verified:
            return
            if len(self.barcode_data) < len(this.barcode_data):
                return
            if len(self.barcode_data_processed) < len(this.barcode_data_processed):
                return
            if not self.document or not self.document_back:
                return
        super(IdentityDocument, self).save(*args, **kwargs)

    def __str__(self):
        return self.full_name + ' documented ' + self.birthday.strftime('%m/%d/%Y')

    def delete(self):
        pass
