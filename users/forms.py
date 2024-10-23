from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django_recaptcha.fields import ReCaptchaField
from feed.middleware import get_current_request
from django.conf import settings
from feed.templatetags.nts import number_to_string
from dateutil.relativedelta import relativedelta
import datetime
from django.contrib.auth import password_validation
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from translate.translate import translate

def get_past_date():
    return datetime.datetime.now() - relativedelta(years=settings.MIN_AGE)

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    in_agreement = forms.BooleanField(required=True)
    of_age = forms.BooleanField(required=True)
    captcha = ReCaptchaField()

    error_messages = {
        "password_mismatch": _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['in_agreement'].label = translate(get_current_request(), mark_safe('By checking this box, you are agreeing to the') + ' <a href="/terms/" title="Read the terms of service and privacy policy">Terms of Service and Privacy Policy</a>.')
        self.fields['of_age'].label = translate(get_current_request(), 'By checking this box, you confirm that you are older than ') + '{} ({})'.format(number_to_string(settings.MIN_AGE), settings.MIN_AGE) + translate(get_current_request(), ' years of age, born on or before {}.'.format(get_past_date().strftime("%B %d, %Y")))
        self.fields['birthday'].initial = get_past_date()

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email']

phone_number_label = 'Phone number (no spaces, parenthesis \'(\' or dashes \'-\', numbers beginning with + only)'

class NonVendorProfileUpdateForm(forms.ModelForm):
    subscribed = forms.BooleanField(required=False)
    phone_number = forms.CharField(required=False)
    def __init__(self, *args, **kwargs):
        super(NonVendorProfileUpdateForm, self).__init__(*args, **kwargs)
        r = get_current_request()
        self.fields['phone_number'].label = translate(r, phone_number_label)
        self.fields['subscribed'].label = translate(r, "Subscribe (uncheck to unsubscribe)")

        if self.instance.subscribed:
            self.fields['subscribed'].initial = True
        if self.instance.enable_two_factor_authentication and not settings.ENFORCE_TFA:
            self.fields['enable_two_factor_authentication'].initial = True
    class Meta:
        model = Profile
        fields = ['phone_number','enable_two_factor_authentication' if not settings.ENFORCE_TFA else 'phone_number', 'subscribed', 'preferred_name', 'name']
        labels = {'name': 'Display name'}


class ProfileUpdateForm(forms.ModelForm):
    subscribed = forms.BooleanField(required=False, label="Subscribe (uncheck to unsubscribe)")
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', error_messages = {'invalid': "Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed."})
    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if self.instance.subscribed:
            self.fields['subscribed'].initial = True
        self.fields['phone_number'].label = phone_number_label
        self.fields['hide_logo'].initial = self.instance.hide_logo
        self.fields['image'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
        self.fields['cover_image'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
    class Meta:
        model = Profile
        fields = ['shake_to_logout', 'hide_logo', 'phone_number', 'enable_facial_recognition_bypass', 'enable_biometrics', 'image', 'cover_image', 'bio', 'subscribed', 'status', 'wishlist', 'shop_url', 'preferred_name', 'name', 'bash', 'email_password']
        labels = {
            'phone_number': 'Phone number (no spaces, parenthesis \'(\' or dashes \'-\', numbers beginning with + only)',
            'name': 'Your display name',
            'wishlist': 'Your Amazon (or other) wishlist',
            'shop_url': 'Your merch shop URL',
            'bash': 'Email username'
        }
        widgets = {
          'status': forms.Textarea(attrs={'rows':3}),
          'bio': forms.Textarea(attrs={'rows':5}),
          'wishlist': forms.Textarea(attrs={'rows':1}),
          'shop_url': forms.Textarea(attrs={'rows':1}),
        }

class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(required=True)

class PhoneNumberForm(forms.Form):
    phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$', error_messages = {'invalid': "Phone number must be entered in the format: '+999999999'. Up to 15 digits is allowed."})
    def __init__(self, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].label = phone_number_label

class TfaForm(forms.Form):
    send_email = forms.BooleanField(required=False)
    code = forms.IntegerField(required=False)
    def __init__(self, *args, **kwargs):
        super(TfaForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'autocomplete': 'off'})
        self.fields['send_email'].initial = True
    help_texts = {
        'code': 'Please enter the six digit code after sending it to your phone or email with the button above.'
    }
