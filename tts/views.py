from django.shortcuts import render, redirect
from tts.models import Word
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.
@login_required
def word(request, word):
    words = Word.objects.filter(word=word).order_by('?') #'-time_processed')
    word = words.first()
    if words.count() == 0:
        return HttpResponse(status=200)
    if word.file_bucket: return redirect(word.file_bucket.url)
    # your other codes ...
    file = open(word.file.path, "rb").read()
    response = HttpResponse(file, content_type="audio/wav")
    response['Content-Disposition'] = 'attachment; filename={}-{}.wav'.format(word.word, word.user.profile.name)
    return response
