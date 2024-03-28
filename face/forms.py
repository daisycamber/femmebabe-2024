from users.models import Profile
import datetime
from django import forms
from .models import Face

class FaceForm(forms.ModelForm):
    class Meta:
        model = Face
        fields = ('image',)