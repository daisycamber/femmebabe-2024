from django import forms
import datetime
from .models import Message

class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = "Message"
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4})
        }
