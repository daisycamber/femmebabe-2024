import os
from django.conf import settings

def get_width(image_path):
    import cv2
    h, w, c = cv2.imread(image_path).shape
    return w

MIN_BC = 30

MIN_BC_NUDE = 60

def blur_faces(input_path):
    import cv2, traceback, math
    bc = math.floor(get_width(input_path)/1000) * 2
    if bc < MIN_BC: bc = MIN_BC
    image = cv2.imread(input_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    try:
        face_detect = cv2.CascadeClassifier(os.path.join(settings.BASE_DIR, 'feed/haarcascade_frontalface_default.xml'))
        face_data = face_detect.detectMultiScale(image, 1.3, 5)
        image = cv2.imread(input_path)
        for (x, y, w, h) in face_data:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 2)
            roi = image[y:y+h, x:x+w]
            roi = cv2.GaussianBlur(roi, (bc + 1,bc + 1), bc*2)
            image[y:y+roi.shape[0], x:x+roi.shape[1]] = roi
        cv2.imwrite(input_path, image)
    except:
        print(traceback.format_exc())


import requests
import json

import base64

def write_image(imgstring, filename):
    import cv2, traceback
    imgdata = base64.b64decode(imgstring)
    with open(filename, 'wb') as f:
        f.write(imgdata)

def blur_nude(input_path, output_path):
    import cv2, traceback, math
    bc = math.floor(get_width(input_path)/1000) * 4
    if bc < MIN_BC_NUDE: bc = MIN_BC_NUDE
    image = cv2.imread(input_path)
    try:
        roi = cv2.GaussianBlur(image, (bc + 1,bc + 1), bc*2)
        cv2.imwrite(output_path, roi)
        return output_path
    except:
        print(traceback.format_exc())


def blur_nude_notworking(input_path, output_path):
    import cv2, traceback
    from nudenet import NudeDetector
    detector = NudeDetector()
    image = cv2.imread(input_path)
    for boxes in detector.detect(input_path)['box']:
        for box in boxes:
            part = image[box[1]:box[3], box[0]:box[2]]
            part = cv2.GaussianBlur(part,(23, 23), 30)
            image[box[1]:box[3], box[0]:box[2]] = part
    cv2.imwrite(output_path, image)

def blur_nude_old(input_path, output_path):
    params = {
        'concepts': 'nudity',
        'api_user': settings.SIGHTENGINE_USER,
        'api_secret': settings.SIGHTENGINE_SECRET
    }
    files = {'media': open(input_path, 'rb')}
    r = requests.post('https://api.sightengine.com/1.0/transform.json', files=files, data=params)
    output = json.loads(r.text)
    if output['status'] == 'success':
        data = output['transform']['base64']
        output_path = output_path + '.' + output['transform']['content-type'].split('/')[1]
        write_image(data, output_path)
        return output_path
