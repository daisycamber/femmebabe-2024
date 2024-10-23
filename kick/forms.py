from django import forms
from django_recaptcha.fields import ReCaptchaField

class AppealForm(forms.Form):
    captcha = ReCaptchaField()
    in_agreement = forms.BooleanField(required=True)
    def __init__(self, *args, **kwargs):
        super(AppealForm, self).__init__(*args, **kwargs)
        self.fields['captcha'].label = 'Prove you are human'
        self.fields['in_agreement'].label = 'By checking this box, I legally swear that I am of age, not in public, and not using the site with intent.'
