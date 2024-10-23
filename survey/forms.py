from django import forms
from .models import Survey, Answer
from feed.middleware import get_current_user

class UpdateSurveyForm(forms.ModelForm):
    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
#    def __init__(self, *args, **kwargs):
#        super(UpdateSurveyForm, self).__init__(*args, *kwargs)
    class Meta:
        model = Survey
        fields = ('priority', 'question', 'answers_seperated')
        labels = {'question': 'A question to ask the user*', 'answers_seperated': 'Answers for the question, one per line*'}

class SurveyForm(forms.ModelForm):
    answer = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'survey-large-text'}),
    )
    def __init__(self, survey, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, *kwargs)
        self.fields['answer'].label = survey.question
        choices = list()
        self.instance.user = get_current_user()
        self.instance.survey = survey
        for c in survey.answers_seperated.split('\n'):
            choices.append((c,c))
        self.fields['answer'].choices = choices
    class Meta:
        model = Answer
        fields = ('answer',)