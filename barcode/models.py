from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
import pytz
import datetime
import uuid, os, shutil
from feed.middleware import get_current_user

def get_document_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}-{}-{}'.format(uuid.uuid4(), instance.timestamp.strftime("%Y%m%d-%H%M%S"), get_current_user().id if get_current_user() else '0'), ext)
    return os.path.join('documents/', filename)


class DocumentScan(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    key = models.TextField(default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan', null=True, blank=True)
    document = models.ImageField(default=None, null=True, blank=True, upload_to=get_document_path)
    document_full = models.ImageField(default=None, null=True, blank=True, upload_to=get_document_path)
    document_isolated = models.ImageField(default=None, null=True, blank=True, upload_to=get_document_path)
    barcode_data = models.TextField(default='')
    idscan = models.TextField(default='')
    barcode_data_processed = models.TextField(default='')
    side = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    birthday = models.DateTimeField(default=timezone.now)
    expiry = models.DateTimeField(default=timezone.now)
    foreign = models.BooleanField(default=False)
    succeeded = models.BooleanField(default=False)
    history = HistoricalRecords()

    def delete(self):
        pass
#        if self.image:
#            os.remove(self.document.path)
#        super(DocumentScan, self).delete()

    def get_base64_image(self):
        with open(str(self.document_isolated.path), mode='rb') as image_file:
            return 'data:image/png;base64,' + base64.b64encode(image_file.read()).decode("utf-8")

    def __str__(self):
        return '{} id {} timestamp {}'.format(self.user.profile.name if self.user else 'none', self.id, self.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime("%m/%d/%Y at %H:%M:%S"))

    def rotate(self):
        from PIL import Image
        img = Image.open(self.document_isolated.path)
        img = img.rotate(180)
        img.save(self.document_isolated.path)
        self.save()

    def save(self, *args, **kwargs):
        from PIL import Image
        from .isolate import write_isolated
        this = DocumentScan.objects.filter(id=self.id).first()
        if this and this.verified: return
        max = settings.BARCODE_SIZE # 500
        super(DocumentScan, self).save(*args, **kwargs)
        if not this or this.document != self.document:
            from lotteh.celery import remove_if_nude
            remove_if_nude.delay(self.id)
            full_path = os.path.join(settings.BASE_DIR, 'media/', get_document_path(self, self.document.name))
            img = Image.open(self.document.path)
            full_path = str(full_path) + '.png'
            img.save(full_path, 'PNG')
            os.remove(self.document.path)
            self.document = full_path
            super(DocumentScan, self).save(*args, **kwargs)
        if not self.document_full:
            path = os.path.join(settings.BASE_DIR, 'media/', get_document_path(self, self.document.name))
            shutil.copy(self.document.path, path)
            self.document_full = path[len(str(settings.BASE_DIR) + '/media/'):]
            super(DocumentScan, self).save(*args, **kwargs)
        if not self.document_isolated:
            path = os.path.join(settings.BASE_DIR, 'media/', get_document_path(self, self.document.name))
            result = write_isolated(self.document_full.path, path)
            if result:
                self.document_isolated = path[len(str(settings.BASE_DIR) + '/media/'):]
                super(DocumentScan, self).save(*args, **kwargs)
        if self.document:
            img = Image.open(self.document.path)
            if img.height > max or img.width > max:
                output_size = (max, max)
                img.thumbnail(output_size)

