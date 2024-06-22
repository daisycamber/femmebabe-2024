from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os, uuid

# Create your models here.
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('melanin/', filename)

class MelaninPhoto(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, related_name="melanin_photos", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    image = models.ImageField(null=True, blank=True, upload_to=get_file_path)

    def delete(self):
        try:
            os.remove(self.image.path)
        except: pass
        super(MelaninPhoto, self).delete()