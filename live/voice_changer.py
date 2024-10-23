import sys, os, uuid
from moviepy.editor import *
import moviepy.editor as mp
from django.conf import settings
from synthesizer.utils import adjust_pitch
from tts.slice import convert_wav

def replace_audio(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    video_with_new_audio = video.set_audio(audio)
    video_with_new_audio.write_videofile(output_path)

def adjust_video_pitch(video_path, output_path, semitones=12):
    temp_wav = convert_wav(video_path)
    replace_audio(video_path, adjust_pitch(temp_wav, semitones), output_path)
    os.remove(temp_wav)
    return output_path
