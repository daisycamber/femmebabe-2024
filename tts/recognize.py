import speech_recognition as sr

# obtain path to "english.wav" in the same folder as this script
from os import path

def audio_to_text(audio_file):
    # use the audio file as the audio source
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)  # read the entire audio file
            return r.recognize_sphinx(audio)
    except:
        return False
