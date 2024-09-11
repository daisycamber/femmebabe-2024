from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    name = forms.CharField(required=False)
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    class Meta:
        model = Contact
        fields = ('name', 'email', 'phone', 'message')
