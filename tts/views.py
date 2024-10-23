from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def word(request, word):
    from django.shortcuts import render, redirect
    from tts.models import Word
    from django.http import HttpResponse
    next_word = request.GET.get('next', '')
    last_word = request.GET.get('next', '')
    from nltk.corpus import wordnet as wn
    word_type = wn.synsets(word)[0].pos()
    next_word_type = None
    last_word_type = None
    try:
        next_word_type = wn.synsets(next_word)[0].pos()
        last_word_type = wn.synsets(last_word)[0].pos()
    except: pass
    words = []
    if next_word_type and last_word_type:
        words = Word.objects.filter(word=word, next_word_type=next_word_type, last_word_type=last_word_type).order_by('?') #'-time_processed')
    if next_word_type:
        words = Word.objects.filter(word=word, next_word_type=next_word_type).order_by('?') #'-time_processed')
    if last_word_type:
        words = Word.objects.filter(word=word, next_word_type=last_word_type).order_by('?') #'-time_processed')
    word = words.first()
    if words.count() == 0:
        return HttpResponse(status=200)
    if word.file_bucket: return redirect(word.file_bucket.url)
    # your other codes ...
    file = open(word.file.path, "rb").read()
    response = HttpResponse(file, content_type="audio/wav")
    response['Content-Disposition'] = 'attachment; filename={}-{}.wav'.format(word.word, word.user.profile.name)
    return response
