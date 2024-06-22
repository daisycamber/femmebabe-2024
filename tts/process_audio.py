import sys
import os
import subprocess
import json
import math

import wave

# tested with VOSK 0.3.15
import vosk
import librosa
import numpy
import pandas

def extract_words(res):
   jres = json.loads(res)
   if not 'result' in jres:
       return []
   words = jres['result']
   return words

def transcribe_words(recognizer, bytes):
    results = []
    chunk_size = 4000
    for chunk_no in range(math.ceil(len(bytes)/chunk_size)):
        start = chunk_no*chunk_size
        end = min(len(bytes), (chunk_no+1)*chunk_size)
        data = bytes[start:end]
        if recognizer.AcceptWaveform(data):
            words = extract_words(recognizer.Result())
            results += words
    results += extract_words(recognizer.FinalResult())
    return results

import subprocess
import os
import sys
import ffmpeg


def convert_video_to_audio_ffmpeg(video_file, output_ext="wav"):
    """Converts video to audio directly using `ffmpeg` command
    with the help of subprocess module"""
    filename, ext = os.path.splitext(video_file)
    subprocess.call(["ffmpeg", "-y", "-i", video_file, f"{filename}.{output_ext}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT)
    return video_file[:-4] + 'wav'

def convert_wav(audio_path):
    return convert_video_to_audio_ffmpeg(audio_path)

def process_user_audio(user, audio_path):
    audio_path = convert_wav(audio_path)

    vosk.SetLogLevel(1)

    model_path = 'vosk-model-small-de-0.15'

    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print('Not a wav')
        return
    sample_rate = 16000
    fr = wf.getframerate()
    print('Framerate is ' + str(fr))
    audio, sr = librosa.load(audio_path, sr=fr)

    # convert to 16bit signed PCM, as expected by VOSK
    int16 = numpy.int16(audio * fr).tobytes()

    # XXX: Model must be downloaded from https://alphacephei.com/vosk/models
    # https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
#    if not os.path.exists(model_path):
#        raise ValueError(f"Could not find VOSK model at {model_path}")

    model = vosk.Model(lang="en-us")
    recognizer = vosk.KaldiRecognizer(model, fr)

    res = transcribe_words(recognizer, int16)
    print(res)
    df = pandas.DataFrame.from_records(res)
    print(df)
#    df = df.sort_values('start')
#    for index, row in df.iterrows():
#        print('Audio at ' + row['start'] + ' ' + row['end'] + ' ' + row['word'])
