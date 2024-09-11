def concat(recording, output_path):
    from .models import get_file_path
    from subprocess import check_output
    import uuid
    import subprocess
    import os, glob
    from django.conf import settings
    from shell.execute import run_command
    from django.core.files.base import ContentFile
    if recording.frames.count() == 0:
        recording.delete()
        return
    import moviepy.editor as moviepy
    from live.logo import add_logo_to_video
    import zipfile
    filename = os.path.join(settings.BASE_DIR, 'temp', str(uuid.uuid4()) + '.txt')
    inputs = ''
    for frame in recording.frames.filter(compressed=True).order_by('time_captured'):
        with zipfile.ZipFile(frame.frame.path, 'r') as zip_ref:
            path = os.path.join(settings.BASE_DIR, '/temp/', str(uuid.uuid4()))
            zip_ref.extractall(path)
            file = os.path.join(path, 'frame.webm')
            new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(frame, 'frame.webm'))
            shutil.copy(file, new_path)
            os.remove(path)
            os.remove(frame.frame.path)
            frame.frame = new_path
            frame.save()
    is_safe = True
    for frame in recording.frames.all().order_by('time_captured'):
        if not frame.still or not os.path.exists(frame.still.path): frame.get_still_url(False)
        if not frame.still or not os.path.exists(frame.still.path): frame.delete()
        else:
            if frame.still and not '*' in recording.camera:
                towrite = frame.still_bucket.storage.open(frame.still.path, mode='wb')
                with frame.still.open('rb') as file:
                    towrite.write(file.read())
                towrite.close()
                frame.still_bucket = frame.still.path
            frame.get_still_thumb_url(False)
            if frame.still_thumbnail:
                towrite = frame.still_thumbnail_bucket.storage.open(frame.still_thumbnail.path, mode='wb')
                with frame.still_thumbnail.open('rb') as file:
                    towrite.write(file.read())
                frame.still_thumbnail_bucket = frame.still_thumbnail.path
                towrite.close()
                if not '*' in recording.camera:
                    os.remove(frame.still.path)
                    os.remove(frame.still_thumbnail.path)
            if frame.frame.name.split('.')[1] != 'mp4':
                path = os.path.join(settings.MEDIA_ROOT, get_file_path(frame, 'frame.mp4'))
                run_command('ffmpeg -i {} -crf 0 -c:v libx264 {}'.format(frame.frame.path, path))
                os.remove(frame.frame.path)
                frame.frame = path
            frame.save()
            inputs = inputs + 'file \'' + frame.frame.path + '\'\n'
        if not frame.safe: is_safe = False
    recording.safe = is_safe
    recording.save()
    if len(inputs) == 0:
        recording.delete()
        return
    with open(filename, 'w') as f:
        f.writelines(inputs)
    #ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp4
#    cmd = 'ffmpeg -f concat -safe 0 -i {} -c copy {}'.format(filename, output_path).split(' ')
    cmd = 'ffmpeg -f concat -safe 0 -i {} -c copy {}'.format(filename, output_path).split(' ')
    check_output(cmd)
    os.remove(filename)
#    run_command('sudo chown love:users ' + str(output_path))
#    cmd = 'ffmpeg -i {} -crf 1 -c:v libx264 {}.mp4'.format(filename, output_path).split(' ')
#    check_output(cmd)
#    os.remove(output_path)
    output_path = str(output_path) + ''
    new_video_path = output_path.split('.')[0] + '-2.mp4'
    add_logo_to_video(output_path, new_video_path)
    os.remove(output_path)
    fileList = glob.glob(str(settings.BASE_DIR) + '*TEMP_MPY_wvf_snd.mp3*', recursive=True)
    for file in fileList:
        try:
            os.remove(file)
        except OSError:
            print("Error while deleting file")
    return new_video_path

def concat_old(recording, output_path):
    clips =[]
    for f in recording.frames.all():
        clips = clips + [moviepy.VideoFileClip(f.frame.path)]
    clip = moviepy.concatenate_videoclips(clips)
    clip.write_videofile(str(output_path) + '.mov', codec='libx264')
    return str(output_path) + '.mov'
