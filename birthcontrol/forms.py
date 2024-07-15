from django import forms
import datetime
from django.utils import timezone
from .models import BirthControlPill, BirthControlProfile
from users.middleware import get_current_user

class BirthControlTimeForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'type': 'date'})) #auto_now=True, auto_now_add=True)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'format': '%H:%M'}))

class BirthControlForm(forms.ModelForm):
    taken_now = forms.BooleanField(required=False)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 9}))
    class Meta:
        model = BirthControlPill
        fields = ('taken_now', 'notes','temperature','taken_with_food','flow','intercourse','incontinence')
    def __init__(self, *args, **kwargs):
        super(BirthControlForm, self).__init__(*args, **kwargs)
        self.fields['notes'].label = 'Notes about how the pill is going (symptoms, mood, pain, etc) - optional'
        dom = int(timezone.now().strftime("%d"))
        ps = int(get_current_user().birthcontrol_profile.period_start)
        self.fields['taken_now'].initial = True
        if dom > ps and dom < ps + 3:
            self.fields['flow'].initial = True

class BirthControlProfileForm(forms.ModelForm):
    reminder_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'format': '%H:%M'}))
    def __init__(self, *args, **kwargs):
        super(BirthControlProfileForm, self).__init__(*args, **kwargs)
        self.fields['birth_control'].label = 'A photo of your birth control showing your prescription label and doctors name'
        self.fields['birth_control_current'].label = 'A current photo of your birth control'
        self.fields['birth_control'].required = True
        self.fields['birth_control_current'].required = True
    class Meta:
        model = BirthControlProfile
        fields = ('birth_control', 'birth_control_current', 'period_start','send_pill_reminder','send_sleep_reminder',)