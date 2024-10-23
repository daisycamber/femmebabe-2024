from django import forms
from .models import Click

def ClickForm(forms.ModelForm):
    class Meta:
        model = Click
        fields = ('path', 'element')
