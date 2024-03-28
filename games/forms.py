from django import forms

class GameForm(forms.Form):
    code = forms.IntegerField(required=False)
    def __init__(self, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)
    help_texts = {
        'code': 'Please enter the code given to you by the other player.'
    }
