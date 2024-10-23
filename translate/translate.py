from django.conf import settings
import traceback
from langdetect import detect, detect_langs
from googletrans import Translator

MAX_TRANS = 1000

def translate(request, content, target=None, language=None):
    if (not content) or content == '' or content == None: return content
    lang = settings.DEFAULT_LANG
    try:
        lang = detect(content)
        langs = detect_langs(content)
        for item in langs:
            if item.lang.startswith(settings.DEFAULT_LANG):
                lang = settings.DEFAULT_LANG
                break
    except: lang = settings.DEFAULT_LANG
    lang_code = None
    if language:
        lang_code = language
    else:
        if hasattr(request, 'LANGUAGE_CODE'):
            lang_code = (request.LANGUAGE_CODE if not request.GET.get('lang', None) else request.GET.get('lang')) if request != None else settings.DEFAULT_LANG
        else:
            lang_code = (settings.DEFAULT_LANG if not request.GET.get('lang', None) else request.GET.get('lang')) if request != None else settings.DEFAULT_LANG
    if target != None: lang_code = target
    if not isinstance(lang_code, str): lang_code = settings.DEFAULT_LANG
    if not lang: lang = settings.DEFAULT_LANG
    lang_code = lang_code.lower()
    if str(lang_code).startswith(str(lang)):
        return content
    from .models import CachedTranslation
    trans = CachedTranslation.objects.filter(src_content=content, src=lang, dest=lang_code).first()
    if trans: return trans.dest_content
    text = ''
    pronunciation = ''
    c = ''
    last = False
    for x in range(0, int(len(content)/MAX_TRANS) + 1):
        try:
            translator = Translator()
            if len(content) < MAX_TRANS:
                trans = translator.translate(content, src=lang, dest=lang_code)
                text = text + str(trans.text)
                pronunciation = pronunciation + str(trans.pronunciation[0]) if hasattr(trans, 'pronunciation') and trans.pronunciation else ''
                break
            if (x+1) * MAX_TRANS > len(content): last = True
            c = content[x * MAX_TRANS - (0 if not c else MAX_TRANS-len(c)):(x+1)*MAX_TRANS - (0 if not c else MAX_TRANS-len(c) if not last else -1 * MAX_TRANS)].rsplit(' ', 1)[0]
            trans = translator.translate(c, src=lang, dest=lang_code)
            text = text + str(trans.text)
            pronunciation = pronunciation + str(trans.pronunciation[0]) if hasattr(trans, 'pronunciation') and trans.pronunciation else ''
        except:
#            print(traceback.format_exc())
            pass
    if len(text) > 0:
        CachedTranslation.objects.get_or_create(src_content=content, dest_content=text, src=lang, dest=lang_code, pronunciation=pronunciation)
    else: return content
    return text
