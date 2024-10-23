from moviepy.editor import AudioFileClip, ImageClip

def audio_to_video(audio_path, image_path, filename):
    audio_clip = AudioFileClip(audio_path, audio_path)
    image_clip = ImageClip(image_path)
    video_clip = VideoClip(image_clip)
    video_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    video_clip.fps = 30
    video_clip.write_videofile(filename)
