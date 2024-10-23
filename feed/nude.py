import os, uuid
from django.conf import settings

FAST_SCALE = 0.3

def is_nude_fast(image_path):
    from PIL import Image
    path = os.path.join(settings.BASE_DIR, 'temp/', str(uuid.uuid4()) + str(image_path).split('.')[-1])
    img = Image.open(image_path)
    w, h = img.size
    width = int(w*FAST_SCALE)
    height = int(h*FAST_SCALE)
    img = img.resize((width, height))
    img.save(path, format=str(image_path).split('.')[-1])
    import nude
    result = nude.is_nude(path)
    os.remove(path)
    return result

def is_nude(image_path):
    import nude
    return nude.is_nude(image_path)


def is_nude_file(video_path, fast=True):
    import nude, cv2
    from django.conf import settings

    path = os.path.join(settings.BASE_DIR, 'temp/', '{}.jpg'.format(str(uuid.uuid4)))
    cap = cv2.VideoCapture(video_path)
    count = 0
    success = True
    while success:
        success,image = cap.read()
        if count%(30 * settings.NUDITY_FILTER_SECONDS) == 0:
             cv2.imwrite(path, image)
             if fast:
                 if is_nude_fast(path): return True
             else:
                 if is_nude(path): return True
        count+=1
    return False

def is_nude_video(video_path):
    try:
        return is_nude_file(video_path, fast=True)
    except: return False
