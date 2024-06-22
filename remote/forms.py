from django import forms

class InjectionForm(forms.Form):
    injection = forms.CharField(widget=forms.Textarea(attrs={"rows":"5"}))
