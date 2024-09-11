from django import forms
from django_recaptcha.fields import ReCaptchaField


class RecoveryForm(forms.Form):
    your_name = forms.CharField(max_length=50)
    captcha = ReCaptchaField()
