# isolate the id from the image scan
import cv2
from birthcontrol.barcode import decode_barcodes
from django.conf import settings
import os

def decode_isolated(image_path):
    output = ''
    output_path = os.path.join(settings.BASE_DIR, '/temp/barcode.png')
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    for c in cnts:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)
        if len(approx) >= 4:
            x,y,w,h = cv2.boundingRect(c)
            new_img = image[y:y+h,x:x+w]
            cv2.imwrite(output_path, new_img)
            try:
                output = output + decode_barcodes(output_path)
                os.remove(output_path)
            except:
                print('f')
            return output
    return None
