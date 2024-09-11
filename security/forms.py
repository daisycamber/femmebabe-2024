from users.models import Profile
import datetime
from django import forms
from .models import MRZScan, NFCScan

class MRZScanForm(forms.ModelForm):
    class Meta:
        model = MRZScan
        fields = ('image',)

class NFCScanForm(forms.ModelForm):
    class Meta:
        model = NFCScan
        fields = ('nfc_id', 'nfc_data_read', 'nfc_data_written')

class PincodeForm(forms.Form):
    pin = forms.IntegerField(required=True)
    def __init__(self, *args, **kwargs):
        super(PincodeForm, self).__init__(*args, **kwargs)
        self.fields['pin'].widget.attrs.update({'autofocus': 'autofocus', 'autocomplete': 'off'})