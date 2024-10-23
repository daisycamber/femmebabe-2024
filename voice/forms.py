from django import forms
import datetime
from voice.models import UserChoice, AudioInteractive
from users.middleware import get_current_user
class AudioInteractiveForm(forms.ModelForm):
    choices = forms.ModelMultipleChoiceField(queryset=None, required=False)
    def __init__(self, *args, **kwargs):
        super(AudioInteractiveForm, self).__init__(*args, **kwargs)
        self.fields['label'].label = "Add a label, cascading to this interactive"
        self.fields['interactive'].label = "Add an interactive message"
        self.fields['choices'].queryset = UserChoice.objects.filter(user=get_current_user())
    class Meta:
        model = AudioInteractive
        fields = ('label','interactive','choices','content')
        widgets = {
          'label': forms.Textarea(attrs={'rows':2}),
          'interactive': forms.Textarea(attrs={'rows':2}),
        }

class ChoiceCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChoiceCreateForm, self).__init__(*args, **kwargs)
        self.fields['option'].label = "Add an option to link to an interactive *"
    class Meta:
        model = UserChoice
        fields = ('option','number')
        widgets = {
          'option': forms.Textarea(attrs={'rows':2}),
        }
