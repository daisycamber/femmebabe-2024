from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
import os, shutil, pytz
from security.secure import get_secure_path
from django.conf import settings
import math

noteStrings = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
A4 = 440
def pitchToNote(frequency):
    noteNum = 12 * (math.log( frequency / A4 )/math.log(2) )
    return round( noteNum ) + 69

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % ('{}-{}'.format(uuid.uuid4(), instance.uploaded_file.strftime("%Y%m%d-%H%M%S")), ext)
    return os.path.join('audio/', filename)

class AudioRecording(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_file = models.DateTimeField(default=timezone.now)
    content = models.FileField(upload_to=get_file_path, null=True, blank=True)
    content_backup = models.FileField(upload_to=get_file_path, null=True, blank=True)
    plot = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    notes = models.TextField(default='', null=True, blank=True)
    transcript = models.TextField(default='', null=True, blank=True)
    post = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    confirmation_id = models.TextField(blank=True)
    pitch_notes = models.TextField(default='', null=True, blank=True)
    pitches = models.TextField(default='', null=True, blank=True)
    volumes = models.TextField(default='', null=True, blank=True)
    session = models.CharField(max_length=32, default='')
    fingerprint = models.TextField(default='', null=True, blank=True)

    def get_secure_url(self):
        path, url = get_secure_path(self.content.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.content.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=60)
        return url

    def get_plot_url(self):
        path, url = get_secure_path(self.plot.name)
        full_path = os.path.join(settings.BASE_DIR, path)
        shutil.copy(self.plot.path, full_path)
        from lotteh.celery import remove_secure
        remove_secure.apply_async([full_path], countdown=60)
        return url

    def get_pitch_code(self):
        return '[{}]'.format(self.pitches)

    def get_note_code(self):
        return '["{}"]'.format(self.pitch_notes.replace(',', '","'))

    def short_time(self):
        return self.uploaded_file.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%H:%M:%S')

    def __str__(self):
        return 'user @ {} {}'.format(self.user.username, self.uploaded_file.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%B %d, %Y %H:%M:%S'))

    def pitch_detect(self):
        from tts.slice import convert_wav
        from scipy.io import wavfile
        from pitch_detectors import algorithms
        import numpy as np
        import soundfile as sf
        import librosa
        new_path = convert_wav(self.content.path)
        fs, a = wavfile.read(new_path)
        pitch = algorithms.Crepe(a, fs)
        pitches = ''
        notes = ''
        volumes = ''
        count = 0
        pc = 0
        pavg = 0
        for p in pitch.f0.astype(np.int64):
            pitch = int(p)
            count = count + 1
            if (count % (int(100/settings.PITCHES_PER_SECOND))) == 0:
                pitch = round(pavg/pc) if pc > 0 else -1
                pitches = pitches + str(pitch) + ','
                notes = notes + ((noteStrings[pitchToNote(pitch) % 12] + str(math.floor(pitchToNote(pitch)/12 - 1))) if pitch > 0 else 'NaN') + ','
                pavg = 0
                pc = 0
                continue
            if pitch > 0:
                pavg = pavg + pitch
                pc = pc + 1
        duration = librosa.get_duration(filename=new_path)
        rms = [np.sqrt(np.mean(block**2)) for block in sf.blocks(new_path, blocksize=int(sf.SoundFile(new_path).frames/(duration/(1.0/settings.PITCHES_PER_SECOND))), overlap=512)]
        for vol in rms:
            volumes = volumes + str(vol) + ','
        pitches = pitches[:-1]
        notes = notes[:-1]
        volumes = volumes[:-1]
        self.pitches = pitches
        self.pitch_notes = notes
        self.volumes = volumes
        self.save()
        os.remove(new_path)

    def delete(self):
        pass
