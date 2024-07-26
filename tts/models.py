from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from audio.models import AudioRecording
from feed.storage import MediaStorage

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('words/', filename)

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class WordStorage(FileSystemStorage):
    def __init__(self, location=None):
        super(WordStorage, self).__init__(location)

    def url(self, name):
        object = Word.objects.get(file=name)
        url = super(WordStorage, self).url(name)
        if self.file_bucket: return self.file_bucket.url
        return reverse('tts:word', kwargs={'word': object.word})


fs = WordStorage()

# Create your models here.
class Word(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='words')
    word = models.TextField(default='', null=True, blank=True)
    last_word = models.TextField(default='', null=True, blank=True)
    next_word = models.TextField(default='', null=True, blank=True)
    word_type = models.CharField(default='', max_length=10, null=True, blank=True)
    next_word_type = models.CharField(default='', max_length=10, null=True, blank=True)
    last_word_type = models.CharField(default='', max_length=10, null=True, blank=True)
    file = models.FileField(upload_to=get_file_path, null=True, blank=True, storage=fs)
    file_bucket = models.FileField(storage=MediaStorage(), upload_to=get_file_path, null=True, blank=True)
    time_processed = models.DateTimeField(default=timezone.now)
    recording = models.ForeignKey(AudioRecording, null=True, on_delete=models.DO_NOTHING, related_name='words')

    def __str__(self):
        return '"{}" - @{}'.format(self.word, self.user)
