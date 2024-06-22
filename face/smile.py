import cv2, os
from django.conf import settings

path_for_smile = os.path.join(settings.BASE_DIR, "face/haarcascade_smile.xml")
def get_smile(image_path):
    image = cv2.imread(image_path)
    smile_cascade = cv2.CascadeClassifier(path_for_smile)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    smile_rects = smile_cascade.detectMultiScale(gray)
    for (x,y,w,h) in smile_rects:
        return (x + w/2, y + h/2)
    return None
