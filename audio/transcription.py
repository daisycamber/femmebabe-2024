def get_transcript(filename):
    import speech_recognition as sr
    from tts.slice import convert_video_to_audio_ffmpeg
    import os
    # open the file
    path = convert_video_to_audio_ffmpeg(filename)
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        try:
            text = r.recognize_google(audio_data)
            os.remove(path)
            return text
        except:
            return ''

def get_wav_transcript(path):
    import speech_recognition as sr
    import os
    # open the file
    r = sr.Recognizer()
    with sr.AudioFile(path) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        try:
            text = r.recognize_google(audio_data)
            return text
        except:
            return ''
