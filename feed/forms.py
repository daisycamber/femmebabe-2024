from django import forms
import datetime
from .models import Post
from feed.middleware import get_current_request
from django_summernote.widgets import SummernoteWidget
from django.conf import settings

def sub_fee(fee):
    import math
    op = ''
    of = len(str(fee))%3
    op = op + str(fee)[0:of] + (',' if of > 0 else '')
    for f in range(math.floor(len(str(fee))/3)):
        op = op + str(fee)[3*f+of:3+3*f+of] + ','
    op = op[:-1]
    return op

def get_pricing():
    from femmebabe.pricing import get_pricing_options
    choices = []
    for option in get_pricing_options(settings.PHOTO_CHOICES):
        choices = choices + [[option, '${}'.format(sub_fee(option))]]
    return choices

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PostForm(forms.ModelForm):
    private = forms.BooleanField(required=False)
    public = forms.BooleanField(required=False)
    content = forms.CharField(widget=SummernoteWidget(attrs={'rows': settings.TEXTAREA_ROWS}), required=False)
    clear_redacted = forms.BooleanField(required=False, widget=forms.HiddenInput)
    recipient = forms.CharField(widget=forms.HiddenInput(), required=False)
    image = MultipleImageField(required=False) #forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True, 'multiple': True}))
    file = MultipleFileField(required=False) #forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True, 'multiple': True}))
    confirmation_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    PHOTO_CHOICES = (
        ('5', '$5'),
        ('10', '$10'),
        ('20', '$20'),
        ('25', '$25'),
        ('50', '$50'),
        ('100', '$100'),
    )
    price = forms.CharField(widget=forms.Select(choices=get_pricing()))

    def __init__(self, *args, **kwargs):
        request = get_current_request()
        super(PostForm, self).__init__(*args, **kwargs)
        if not self.instance: self.fields['price'].initial = get_current_request().user.vendor_profile.photo_tip[1:]
        if get_current_request().GET.get('raw', None): self.fields['content'].widget = forms.Textarea(attrs={'rows': settings.TEXTAREA_ROWS})
        self.fields['image'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
        self.fields['file'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
        if request.GET.get('camera'):
            self.fields['image'].widget.attrs.update({'capture': 'user'})
            self.fields['file'].widget.attrs.update({'accept': 'video/*', 'capture': 'user'})
        if request.GET.get('audio'):
            self.fields['file'].widget.attrs.update({'accept': 'audio/*', 'capture': 'user'})
        if self.instance and self.instance.content:
            self.fields['clear_redacted'].widget = forms.CheckboxInput()
        if self.instance and self.instance.private:
            qs = []
            if self.instance.recipient:
                self.fields['recipient'].initial = str(self.instance.recipient.id)
            qs = qs + [('0', 'No recipient')]
            for q in self.instance.author.subscriptions.all():
                qs = qs + [(str(q.id), '+ ' + q.name)]
            self.fields['recipient'].widget = forms.Select(choices=qs)
        if self.instance.pk == None:
            self.fields['public'].widget=forms.CheckboxInput(attrs={'checked': True})

    class Meta:
        model = Post
        fields = ('feed', 'content', 'image', 'clear_redacted', 'file', 'price', 'private', 'public', 'pinned', 'confirmation_id')

class ScheduledPostForm(forms.ModelForm):
    date = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={'type': 'date'})) #auto_now=True, auto_now_add=True)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'format': '%H:%M'}))
    image = MultipleImageField(required=False) #forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True, 'multiple': True}))
    file = MultipleFileField(required=False) #forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True, 'multiple': True}))
    content = forms.CharField(widget=SummernoteWidget(attrs={'rows': settings.TEXTAREA_ROWS}), required=False)
    clear_redacted = forms.BooleanField(required=False, widget=forms.HiddenInput)
    recipient = forms.CharField(widget=forms.HiddenInput(), required=False)
    confirmation_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    PHOTO_CHOICES = (
        ('5', '$5'),
        ('10', '$10'),
        ('20', '$20'),
        ('25', '$25'),
        ('50', '$50'),
        ('100', '$100'),
    )
    price = forms.CharField(widget=forms.Select(choices=get_pricing()))

    def __init__(self, *args, **kwargs):
        request = get_current_request()
        super(ScheduledPostForm, self).__init__(*args, **kwargs)
        if not self.instance: self.fields['price'].initial = get_current_request().user.vendor_profile.photo_tip[1:]
        if get_current_request().GET.get('raw', None): self.fields['content'].widget = forms.Textarea(attrs={'rows': settings.TEXTAREA_ROWS})
        self.fields['image'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
        self.fields['file'].widget.attrs.update({'style': 'width:100%;padding:25px;border-style:dashed;border-radius:10px;'})
        if request.GET.get('camera'):
            self.fields['image'].widget.attrs.update({'capture': 'user'})
            self.fields['file'].widget.attrs.update({'accept': 'video/*', 'capture': 'user'})
        if request.GET.get('audio'):
            self.fields['file'].widget.attrs.update({'accept': 'audio/*', 'capture': 'user'})
        if self.instance and self.instance.content:
            self.fields['clear_redacted'].widget = forms.CheckboxInput()
        if self.instance and self.instance.private:
            qs = []
            if self.instance.recipient:
                self.fields['recipient'].initial = str(self.instance.recipient.id)
            qs = qs + [('0', 'No recipient')]
            for q in self.instance.author.subscriptions.all():
                qs = qs + [(str(q.id), '+ ' + q.name)]
            self.fields['recipient'].widget = forms.Select(choices=qs)
        if self.instance.pk == None:
            self.fields['public'].widget=forms.CheckboxInput(attrs={'checked': True})

    class Meta:
        model = Post
        fields = ('feed', 'content', 'image', 'clear_redacted', 'file', 'price', 'private', 'public', 'pinned', 'confirmation_id')

class UpdatePostForm(ScheduledPostForm):
    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))
    file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))
