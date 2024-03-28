from django import forms

class EditAudioForm(forms.Form):
    revert = forms.BooleanField(required=False)
    add_pitch_adjust = forms.BooleanField(required=False)
    pitch_adjust = forms.IntegerField(required=False)
    add_reverb = forms.BooleanField(required=False)
    reverb = forms.FloatField(required=False)
    add_reverb = forms.BooleanField(required=False)
    compress = forms.BooleanField(required=False)
    threshold_db = forms.IntegerField(required=False)
    ratio = forms.IntegerField(required=False)
    highpass = forms.BooleanField(required=False)
    highpass_cutoff_hz = forms.IntegerField(required=False)
    lowpass = forms.BooleanField(required=False)
    lowpass_cutoff_hz = forms.IntegerField(required=False)
    gain_db = forms.IntegerField(required=False)
    normalize = forms.BooleanField(required=False)
    def __init__(self, *args, **kwargs):
        super(EditAudioForm, self).__init__(*args, **kwargs)
        self.fields['pitch_adjust'].initial = 12
        self.fields['reverb'].initial = 0.25
        self.fields['threshold_db'].initial = -50
        self.fields['ratio'].initial = 25
        self.fields['highpass_cutoff_hz'].initial = 600
        self.fields['lowpass_cutoff_hz'].initial = 500
        self.fields['gain_db'].initial = 0
