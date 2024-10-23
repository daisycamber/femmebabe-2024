from django.db import models
from django.contrib.auth.models import User
import uuid, os
from django.utils import timezone
from django.conf import settings

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}'.format(uuid.uuid4()), ext)
    return os.path.join('synthesizer/', filename)

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    identifier = models.CharField(max_length=100, default=uuid.uuid4)
    name = models.CharField(default='', max_length=100)
    last_updated = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING, related_name='projects')
    file = models.FileField(upload_to=get_file_path, max_length=100, null=True, blank=True)
    bpm = models.IntegerField(default=120)
    volume = models.IntegerField(default=100)

    def compile(self, format):
        path = os.path.join(settings.BASE_DIR, get_file_path(self, 'name.{}'.format(format)))
        from pydub import AudioSegment, effects
        combined = AudioSegment.empty()
        for sound in self.sounds.all():
            sound_segment = AudioSegment.from_file(sound.file.path)
            combined = combined.overlay(sound_segment, sound.index)
        effects.normalize(combined)
        combined.export(path, format=format)
        self.file = path
        self.save()

    def delete(self):
        if self.file:
            os.remove(self.file.path)
        super(Profile, self).delete()


class Midi(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='midi')
    length = models.IntegerField(default=4)
    track = models.IntegerField(default=0)
    file = models.FileField(upload_to=get_file_path, max_length=100, null=True, blank=True)

class Note(models.Model):
    id = models.AutoField(primary_key=True)
    midi = models.ForeignKey(Midi, on_delete=models.CASCADE, related_name='notes')
    index = models.FloatField(default=0) # in 1/32 notes
    length = models.IntegerField(default=8) # in 1/32 notes
    pitch = models.CharField(max_length=4)

class Position(models.Model):
    id = models.AutoField(primary_key=True)
    midi = models.ForeignKey(Midi, on_delete=models.CASCADE, related_name='position')
    track = models.IntegerField(default=0)
    index = models.FloatField(default=0)
    length = models.IntegerField(default=4)

class Sound(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sounds')
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    index = models.FloatField(default=0)
    track = models.IntegerField(default=0)

    def delete(self):
        if self.file:
            os.remove(self.file.path)
        super(Sound, self).delete()

class Synth(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='synths')
    name = models.CharField(default='', max_length=100)
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    index = models.FloatField(default=0)
    volume = models.IntegerField(default=0)
    gain = models.IntegerField(default=0)
    length = models.IntegerField(default=0)
    distortion = models.IntegerField(default=0)
    highpass_filter = models.IntegerField(default=0)
    lowpass_filter = models.IntegerField(default=0)
    compressor = models.IntegerField(default=0)
    delay = models.IntegerField(default=0)
    reverb = models.IntegerField(default=0)
    pitch_adjust = models.IntegerField(default=0)
    fade = models.IntegerField(default=0)
    mode = models.IntegerField(default=0)
    instrument = models.IntegerField(default=0)
    continuous_pitch = models.IntegerField(default=0)

    def delete(self):
        super(Synth, self).delete()
