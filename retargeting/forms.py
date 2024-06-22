from django import forms
import datetime
from django.utils import timezone
from .models import ScheduledEmail
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from django.core.validators import MinLengthValidator

class EmailForm(forms.ModelForm):
    date = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'format': '%H:%M'}))
    content = forms.CharField(required=True, widget=SummernoteWidget(attrs={'rows': 9, 'style': 'background-color: #55555 !important;'}), validators=[MinLengthValidator(20)], max_length=500)
    subject = forms.CharField(required=True, validators=[MinLengthValidator(10)], max_length=60)

    class Meta:
        model = ScheduledEmail
        fields = ('subject', 'content', 'date', 'time')