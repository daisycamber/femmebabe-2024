# Python code to convert video to audio
import moviepy.editor as mp
import speech_recognition as sr
import uuid
from django.conf import settings
import os

def get_transcript(mp4_file):
    # Insert Local Video File Path
    clip = mp.VideoFileClip(mp4_file)
    output_wav = os.path.join(settings.BASE_DIR, "temp/data/{}.wav".format(str(uuid.uuid4())))
    # Insert Local Audio File Path
    clip.audio.write_audiofile(output_wav,codec='pcm_s16le')
    # initialize the recognizer
    r = sr.Recognizer()
    # open the file
    with sr.AudioFile(output_wav) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data)
        os.remove(output_wav)
        return text
