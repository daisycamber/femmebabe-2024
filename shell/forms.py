from django import forms

class CommandForm(forms.Form):
    input = forms.CharField(max_length=10000)
    def __init__(self, *args, **kwargs):
        super(CommandForm, self).__init__(*args, **kwargs)
        self.fields['input'].widget.attrs.update({'spellcheck': 'false', 'autocapitalize': 'none', 'autofocus': 'autofocus', 'autocomplete': 'off'})

class EditFileForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 18}))
    length = forms.IntegerField(widget=forms.HiddenInput())
    def __init__(self, *args, **kwargs):
        super(EditFileForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'spellcheck': 'false', 'autocapitalize': 'none', 'autocomplete': 'off'})
