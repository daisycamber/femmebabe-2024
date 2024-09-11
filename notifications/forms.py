from django import forms

class NotificationForm(forms.Form):
    head = forms.CharField(required=False, max_length=63)
    body = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 5}))
    url = forms.CharField(required=False, max_length=120)
    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)