from sewar.full_ref import mse
import cv2

def similarity(i1, i2):
    img1 = cv2.imread(i1)
    height, width, dim = img1.shape
    img2 = cv2.imread(i2)
    dim = (width, height)
    resized = None
    try:
        resized = cv2.resize(img2, dim, interpolation = cv2.INTER_AREA)
    except: return False
    return mse(img1, resized) < 5 * (width/1920)