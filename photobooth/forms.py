from django import forms

class RemoteForm(forms.Form):
    time = forms.IntegerField()
    def __init__(self, *args, **kwargs):
        super(RemoteForm, self).__init__(*args, **kwargs)
        self.fields['time'].initial = 0
