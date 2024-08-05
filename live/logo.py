def add_logo_to_video(video_path, new_video_path):
    import moviepy.editor as mp
    from django.conf import settings
    import os
    import glob
    video = mp.VideoFileClip(video_path)
    logo = (mp.ImageClip(os.path.join(settings.BASE_DIR, "media/static/lotteh.png"))
              .set_duration(video.duration)
              .resize(height=int(video.w/13)) # if you need to resize...
              .margin(right=8, top=8, opacity=0) # (optional) logo-border padding
              .set_pos(("left","bottom")))
    final = mp.CompositeVideoClip([video, logo])
    final.write_videofile(new_video_path)
    for f in glob.glob(str(settings.BASE_DIR) + '*TEMP_MPY_wvf_snd.mp3'):
        os.remove(f)
    return new_video_path
