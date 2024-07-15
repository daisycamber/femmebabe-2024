from django import forms
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from feed.middleware import get_current_request
from users.middleware import get_current_user
from .models import Choices, Choice, UserChoice

class ChoicesForm(forms.Form):
    choice = forms.CharField()
#widget=forms.Select(choices=CHOICES))
    def __init__(self, *args, **kwargs):
        super(ChoicesForm, self).__init__(*args, **kwargs)
        CHOICES = list()
        objects = Choices.objects.filter(interactive=get_current_request().user.profile.interactive)
        object = objects.first()
        if not object:
            user = get_current_request().user
            user.profile.interactive = 'What would you like me to do?'
            objects = Choices.objects.filter(interactive=user.profile.interactive)
            object = objects.first()
        for choice in object.choices.all():
            CHOICES.append((choice.option, choice.option))
        CHOICES = tuple(CHOICES)
        self.fields['choice'].label = object.interactive
        self.fields['choice'].widget = forms.Select(choices=CHOICES)
    class Meta:
        fields = ['choice']

class ChoicesCreateForm(forms.ModelForm):
    choices = forms.ModelMultipleChoiceField(queryset=UserChoice.objects.all())
    def __init__(self, *args, **kwargs):
        super(ChoicesCreateForm, self).__init__(*args, **kwargs)
        self.fields['choices'].label = "Add options for this interactive that will cascade to another interactive"
        self.fields['label'].label = "Add a label that will cascade to this interactive"
        self.fields['label'].init = self.instance.label or ''
    class Meta:
        model = Choices
        fields = ('choices','label', )
        widgets = {
          'label': forms.Textarea(attrs={'rows':2}),
        }

class ChoiceCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChoiceCreateForm, self).__init__(*args, **kwargs)
        self.fields['option'].label = "Add an option to link to an interactive *"
    class Meta:
        model = UserChoice
        fields = ('option',)
        widgets = {
          'option': forms.Textarea(attrs={'rows':2}),
        }
