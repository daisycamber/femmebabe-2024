from django import forms
from .models import MelaninPhoto

class MelaninPhotoForm(forms.ModelForm):
    class Meta:
        model = MelaninPhoto
        fields = ('image',)