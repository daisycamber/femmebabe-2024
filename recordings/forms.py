from django import forms
import datetime
from live.models import VideoRecording, VideoFrame

class RecordingInteractiveForm(forms.ModelForm):
    frames = forms.ModelMultipleChoiceField(queryset=None)
    def __init__(self, *args, **kwargs):
        super(RecordingInteractiveForm, self).__init__(*args, **kwargs)
        self.fields['interactive'].label = "Add an interactive message"
        self.fields['frames'].queryset = VideoFrame.objects.filter(user=self.instance.user) #self.instance.frames.all()
    class Meta:
        model = VideoRecording
        fields = ('interactive','frames')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2})
        }
