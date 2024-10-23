import cv2
from tensorflow.keras.preprocessing.image import img_to_array
import os
import numpy as np
from tensorflow.keras.models import model_from_json
import traceback
from django.conf import settings

root_dir = os.getcwd()
# Load Face Detection Model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
base_path = os.path.join(settings.BASE_DIR, 'face/antispoofing/')
# Load Anti-Spoofing Model graph
json_file = open(base_path + 'antispoofing_models/antispoofing_model.json','r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
# load antispoofing model weights
model.load_weights(base_path + 'antispoofing_models/antispoofing_model.h5')
print("Model loaded from disk")

def is_live(image_path):
    label = 'spoof'
    try:
        frame = cv2.imread(image_path)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray,1.3,5)
        for (x,y,w,h) in faces:
            face = frame[y-5:y+h+5,x-5:x+w+5]
            resized_face = cv2.resize(face,(160,160))
            resized_face = resized_face.astype("float") / 255.0
            # resized_face = img_to_array(resized_face)
            resized_face = np.expand_dims(resized_face, axis=0)
            # pass the face ROI through the trained liveness detector
            # model to determine if the face is "real" or "fake"
            preds = model.predict(resized_face)[0]
            print('Liveness prediction ' + str(preds))
            if preds > settings.FACE_LIVENESS_ZERO_TO_ONE: #0.5:
                return False
    except Exception as e:
        print(e)
        pass
    return True
