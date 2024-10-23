import os
import cv2
import math
import pandas as pd
from PIL import Image
import numpy as np
from django.conf import settings
import traceback

MIN_TO_ROTATE = 90

opencv_home = cv2.__file__

folders = opencv_home.split(os.path.sep)[0:-1]

path = folders[0]

for folder in folders[1:]:
    path = path + "/" + folder

path_for_face = path+"/data/haarcascade_frontalface_alt2.xml"
path_for_eyes = path+"/data/haarcascade_eye.xml"
path_for_nose = os.path.join(settings.BASE_DIR, "vision/haarcascade_mcs_nose.xml")
path_for_mouth = os.path.join(settings.BASE_DIR, "face/haarcascade_mcs_mouth.xml")

face_detector = cv2.CascadeClassifier(path_for_face)
eye_detector = cv2.CascadeClassifier(path_for_eyes)
nose_detector = cv2.CascadeClassifier(path_for_nose)
mouth_detector = cv2.CascadeClassifier(path_for_mouth)

def get_gray(img_path):
    img = cv2.imread(img_path)
    image = Image.open(img_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
        image.save(img_path)
    mode = Image.open(img_path).mode[0]
    print('Image mode {}'.format(mode))
    img = cv2.imread(img_path)
    if mode == 'R':
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def has_features(img_path):
    img_raw = cv2.imread(img_path).copy()
#    img, gray_img = face_detection(cv2.imread(img_path))
    gray_img = get_gray(img_path)
    eyes = eye_detector.detectMultiScale(gray_img)
    try:
        if len(eyes) == 2 and get_nose(gray_img) and get_mouth(gray_img):
            return True
        elif len(eyes) < 2:
            print('Didn\'t detect eyes.')
    except: print(traceback.format_exc())
    return False

def face_detection(img_path):
    img = cv2.imread(img_path)
    faces = face_detector.detectMultiScale(img, 1.1, 4)
    img_gray = get_gray(img_path)
    if (len(faces) <= 0):
        return img, img_gray
    else:
        X, Y, W, H = faces[0]
        img = img[int(Y):int(Y+H), int(X):int(X+W)]
        return img, img_gray[int(Y):int(Y+H), int(X):int(X+W)]


def trignometry_for_distance(a, b):
    return math.sqrt(((b[0] - a[0]) * (b[0] - a[0])) + ((b[1] - a[1]) * (b[1] - a[1])))

def face_rotation(img_path):
    img_raw = cv2.imread(img_path).copy()
    img, gray_img = face_detection(img_path)
    eyes = eye_detector.detectMultiScale(gray_img)
    eyes_above_nose = 0
    try:
        nosex, nosey = get_nose(img_raw)
        for (x,y,w,h) in eyes:
            if y + h/2 < nosey:
                eyes_above_nose = eyes_above_nose + 1
    except: pass
    if eyes_above_nose >= 2:
        return 0
    img_raw = cv2.imread(img_path).copy()
    img_raw = cv2.rotate(img_raw, cv2.ROTATE_180)
    img, gray_img = face_detection(img_path)
    eyes = eye_detector.detectMultiScale(gray_img)
    eyes_above_nose = 0
    try:
        nosex, nosey = get_nose(img_raw)
        for (x,y,w,h) in eyes:
            if y + h/2 < nosey:
                eyes_above_nose = eyes_above_nose + 1
    except: pass
    if eyes_above_nose >= 2:
        return 2
    img_raw = cv2.imread(img_path).copy()
    img_raw = cv2.rotate(img_raw, cv2.ROTATE_90_CLOCKWISE)
    img, gray_img = face_detection(img_path)
    eyes = eye_detector.detectMultiScale(gray_img)
    eyes_above_nose = 0
    try:
        nosex, nosey = get_nose(img_raw)
        for (x,y,w,h) in eyes:
            if y + h/2 < nosey:
                eyes_above_nose = eyes_above_nose + 1
    except: pass
    if eyes_above_nose >= 2:
        return 1
    img_raw = cv2.imread(img_path).copy()
    img_raw = cv2.rotate(img_raw, cv2.ROTATE_90_COUNTERCLOCKWISE)
    img, gray_img = face_detection(img_path)
    eyes = eye_detector.detectMultiScale(gray_img)
    eyes_above_nose = 0
    try:
        nosex, nosey = get_nose(img_raw)
        for (x,y,w,h) in eyes:
            if y + h/2 < nosey:
                eyes_above_nose = eyes_above_nose + 1
    except: pass
    if eyes_above_nose >= 2:
        return -1
    return 0

def face_angle_detect(image_path):
    img_raw = cv2.imread(image_path)
    return face_rotation_detect(image_path, 0, True)

def face_rotation_detect(img_path, base, ang=None):
    direction = 0
    angle = 0
    img, gray_img = face_detection(img_path)
    eyes = eye_detector.detectMultiScale(gray_img)

    if len(eyes) >= 2:
        eye = eyes[:, 2]
        container1 = []
        for i in range(0, len(eye)):
            container = (eye[i], i)
            container1.append(container)
        df = pd.DataFrame(container1, columns=["length", "idx"]).sort_values(by=['length'])
        eyes = eyes[df.idx.values[0:2]]
        eye_1 = eyes[0]
        eye_2 = eyes[1]
        if eye_1[0] > eye_2[0]:
            left_eye = eye_2
            right_eye = eye_1
        else:
            left_eye = eye_1
            right_eye = eye_2
        right_eye_center = (
            int(right_eye[0] + (right_eye[2]/2)),
            int(right_eye[1] + (right_eye[3]/2)))

        right_eye_x = right_eye_center[0]
        right_eye_y = right_eye_center[1]

        left_eye_center = (
            int(left_eye[0] + (left_eye[2] / 2)),
            int(left_eye[1] + (left_eye[3] / 2)))
        left_eye_x = left_eye_center[0]
        left_eye_y = left_eye_center[1]

        if left_eye_y > right_eye_y:
            point_3rd = (right_eye_x, left_eye_y)
            direction = -1  # rotate image direction to clock
        else:
            point_3rd = (left_eye_x, right_eye_y)
            direction = 1  # rotate inverse direction of clock
        a = trignometry_for_distance(left_eye_center,
                                     point_3rd)
        b = trignometry_for_distance(right_eye_center,
                                     point_3rd)
        c = trignometry_for_distance(right_eye_center,
                                     left_eye_center)
        try:
            cos_a = (b*b + c*c - a*a)/(2*b*c)
            angle = (np.arccos(cos_a) * 180) / math.pi
            if direction == -1:
                angle = 90 - angle
            else:
                angle = -(90-angle)
        except: pass
    print(direction)
    print('Angle is ' + str(angle))
    if ang: return angle
    if base: return base
    return direction if abs(angle) > MIN_TO_ROTATE else 0

def get_nose(gray):
    nose_cascade = cv2.CascadeClassifier(path_for_nose)
    nose_rects = nose_cascade.detectMultiScale(gray)
    for (x,y,w,h) in nose_rects:
        return (x + w/2, y + h/2)
    print('Didn\'t detect nose')
    return None

def get_mouth(gray):
    mouth_cascade = cv2.CascadeClassifier(path_for_mouth)
    mouth_rects = mouth_cascade.detectMultiScale(gray)
    for (x,y,w,h) in mouth_rects:
        return (x + w/2, y + h/2)
    print('Didn\'t detect mouth')
    return None
