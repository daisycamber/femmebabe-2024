from django import forms
from .models import IdentityDocument
from django.utils import timezone
import datetime
from django.conf import settings
from dateutil.relativedelta import relativedelta
from feed.middleware import get_current_user, get_current_request
from jsignature.forms import JSignatureField, JSignatureWidget
from feed.middleware import get_current_request
from translate.translate import translate

def get_past_date():
    return datetime.datetime.now() - relativedelta(years=settings.MIN_AGE_VERIFIED)

class VerificationForm(forms.ModelForm):
    document_number = forms.CharField(widget=forms.TextInput())
    birthday = forms.DateField(initial=get_past_date, widget=forms.DateInput(attrs={'type': 'date'}))
    signature = JSignatureField(widget=JSignatureWidget(jsignature_attrs={'color': '#ff0000' if get_current_user() and not get_current_user().profile.vendor else '#000000'}))
    i_am_a = forms.CharField()
    seeking = forms.CharField()
    attest = forms.BooleanField()
    def __init__(self, *args, **kwargs):
        super(VerificationForm, self).__init__(*args, **kwargs)
        r = get_current_request()
        self.fields['document'].required = True
        self.fields['address'].required = True
        self.fields['document_number'].required = True
        self.fields['document_back'].required = True
        self.fields['full_name'].required = True
        self.fields['document'].label = translate(r, 'Upload a photo of your drivers license or state ID document clearly showing your full name and date of birth.')
        self.fields['address'].label = translate(r, 'Let me know where you live')
        self.fields['full_name'].label = translate(r, 'Please tell me your full name, first, middle and last name.')
        self.fields['document_number'].label = translate(r, 'The ID number on your document')
        self.fields['document_back'].label = translate(r, 'Upload a photo of the back of your ID document clearly showing the PDF417 barcode.')
        self.fields['birthday'].label = translate(r, 'Tell me your birthday (as the day is shown on your ID)')
        self.fields['birthday'].initial = get_past_date()
        self.fields['attest'].label = translate(r, 'I confirm and attest to my own good character and compliance with the law as well as the policies listed on this website.')
        i = [('Woman','Woman'), ('Man','Man'), ('Heat','Heat')]
        s = [('Woman','Woman'), ('Man','Man'), ('Missile','Missile')]
        self.fields['i_am_a'].widget = forms.Select(choices=i)
        self.fields['seeking'].widget = forms.Select(choices=s)
        if get_current_request().GET.get('camera'):
            self.fields['document'].widget.attrs.update({'capture': 'environment'})
            self.fields['document_back'].widget.attrs.update({'capture': 'environment'})
        self.fields['document'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
        self.fields['document_back'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
    class Meta:
        model = IdentityDocument
        fields = ['full_name','birthday','address','document_number','document','document_back', 'i_am_a', 'seeking', 'signature', 'attest']
        widgets = {
            'birthday': forms.DateInput(),
            'document_number': forms.Textarea(attrs={'rows': 1}),
        }
