import numpy as np
import cv2
from PIL import Image

def get_image_contours(image_path):
    # Read the image and perfrom an OTSU threshold
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert("RGB")
        image.save(image_path)
    img = cv2.imread(image_path)
    kernel = np.ones((15,15),np.uint8)
    # Perform closing to remove hair and blur the image
    closing = cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel, iterations = 2)
    blur = cv2.blur(closing,(15,15))
    # Binarize the image
    gray = cv2.cvtColor(blur,cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    # Search for contours and select the biggest one
    _, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    points = []
    for c in contours:
        x,y,w,h = cv2.boundingRect(c)
        points = points + [[x + w/2, y + h/2]]
    return points