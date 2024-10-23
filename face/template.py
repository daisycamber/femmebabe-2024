import cv2
import numpy as np

def is_template(i1, i2):
    img_rgb = cv2.imread(i1)
    template = cv2.imread(i2)
    w, h = template.shape[:-1]
    dim = (template.shape[1], template.shape[0])
    resized = cv2.resize(img_rgb, dim, interpolation = cv2.INTER_AREA)
    res = cv2.matchTemplate(resized, template, cv2.TM_CCOEFF_NORMED)
    threshold = .6
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        print('Pt is ' + str(pt))
        return True
    return False
