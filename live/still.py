import os
from django.conf import settings

def get_width(video_path):
    import cv2
    cap = cv2.VideoCapture(video_path)
    return cap.get(cv2.CAP_PROP_FRAME_WIDTH)

def is_still(input_path):
    import cv2
    from sewar.full_ref import uqi, mse
    vidcap = cv2.VideoCapture(input_path)
    width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
    success,image = vidcap.read()
    first = True
    lastimg = None
    firstimg = None
    width = None
    height = None
    while success:
        success,image = vidcap.read()
        if first and success:
            first = False
            firstimg = image.copy()
            try:
                width = int(firstimg.shape[1])
                height = int(firstimg.shape[0])
            except: first = True
        elif success:
            lastimg = image
    dim = (width, height)
    resized = None
    try:
        resized = cv2.resize(lastimg, dim, interpolation = cv2.INTER_AREA)
    except:
        return False, -1
    result = mse(firstimg, resized)
    print("MSE: " + str(result))
    still = result < int(width)/192 * settings.CV2_MSE_DIV
    print('Is still? ' + str(still))
    return still, result

def get_still(input_path, output_path):
    vidcap = cv2.VideoCapture(input_path)
    success = True
    firstimg = None
    first = True
    while success:
        success,image = vidcap.read()
        if first and success:
            first = False
            firstimg = image.copy()
            try:
                width = int(firstimg.shape[1])
                height = int(firstimg.shape[0])
                cv2.imwrite(output_path, firstimg)
                if os.path.exists(output_path):
                    return output_path
                else:
                    first = True
            except: first = True
    return None
