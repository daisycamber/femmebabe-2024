import cv2 as cv

def denoise(image_path):
    img = cv.imread(image_path)
    dst = cv.fastNlMeansDenoisingColored(img,None,3,3,7,21)
    cv.imwrite(image_path, dst)
