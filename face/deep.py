import json
from django.conf import settings

models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib"]

use_models = [0,1,2,6]

#use_models = [1]

NUM_FACES = 5

MIN_AGE = settings.MIN_AGE_VERIFIED

#PASSING = 75/100.0
PASSING = settings.FACE_PASSING_SCORE

PEAK_FEAR = 20

PEAK_HAPPY = 3

def is_face(face_path):
    from deepface import DeepFace
    try: return len(DeepFace.extract_faces(face_path, detector_backend=models[7].lower())) == 1
    except: return False
#    faces = DeepFace.detectFace(img_path=face_path, enforce_detection=False, detector_backend='opencv') # target_size = (X,Y)
#    for face in faces:
#        for fac in face:
#            for fa in fac:
#                if abs(fa) > 0:
#                    return True
#    return False

def verify_face_score(face_path, faces):
    from deepface import DeepFace
    if len(faces) > NUM_FACES:
        faces = faces[:NUM_FACES]
    fail_count = 0
    total_score = len(use_models) * len(faces)
    for model in use_models:
        for face in faces:
            import os
            try:
                if not face.image or not os.path.exists(face.image.path): face.download_photo()
                result = DeepFace.verify(img1_path=face_path, img2_path=face.image.path, model_name=models[model])
                if not result['verified']:
                    fail_count = fail_count + 1
            except: pass
    return (total_score-fail_count)/total_score

def verify_face(face_path, faces):
    from deepface import DeepFace
    if len(faces) > NUM_FACES:
        faces = faces[:NUM_FACES]
    fail_count = 0
    total_score = len(use_models) * len(faces)
    for model in use_models:
        for face in faces:
            try:
                result = DeepFace.verify(img1_path=face_path, img2_path=face.image.path, model_name=models[model])
                if not result['verified']:
                    fail_count = fail_count + 1
            except: pass
    print('Score ' + str((total_score-fail_count)/total_score))
    if (total_score-fail_count)/total_score >= PASSING:
        print('Identified face.')
        return True
    print('Failed to identify face.')
    return False




def verify_emotion(face_path):
    from deepface import DeepFace
    obj = DeepFace.analyze(img_path=face_path, actions=['gender','emotion'])[0]
    print(obj)
    if obj["emotion"]["happy"] > PEAK_HAPPY or obj["emotion"]["fear"] > PEAK_FEAR or obj["dominant_emotion"] == "happy":
        return False
    return True

def verify_age(face_path):
    from deepface import DeepFace
    try:
        obj = DeepFace.analyze(img_path=face_path, actions=['age'])[0]
        if obj["age"] < MIN_AGE:
            return False
        print(obj)
    except: pass
    return True

def verify_age_cv2(img):
    from deepface import DeepFace
    try:
        obj = DeepFace.analyze(img, actions=['age'])[0]
        print(obj)
        if obj["age"] < MIN_AGE:
            return False
    except: pass
    return True
