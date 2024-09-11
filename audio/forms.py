from django import forms
import datetime
from .models import AudioRecording

class AudioRecordingForm(forms.ModelForm):
    generate_speech = forms.BooleanField(initial=True, required=False)
    generate_transcript = forms.BooleanField(initial=True, required=False)
    live = forms.BooleanField(initial=False, required=False)
    pitches = forms.CharField(widget=forms.HiddenInput(), required=False)
    volumes = forms.CharField(widget=forms.HiddenInput(), required=False)
    pitch_notes = forms.CharField(widget=forms.HiddenInput(), required=False)
    session = forms.CharField(widget=forms.HiddenInput())
    content = forms.FileField(required=True)

    class Meta:
        model = AudioRecording
        fields = ('live', 'notes', 'public', 'post', 'content', 'generate_speech','generate_transcript', 'pitches', 'volumes', 'pitch_notes', 'session')