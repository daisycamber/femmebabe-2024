from users.models import Profile
import datetime
from django import forms
from .models import DocumentScan

class ScanForm(forms.ModelForm):
    key = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = DocumentScan
        fields = ('key', 'document',)