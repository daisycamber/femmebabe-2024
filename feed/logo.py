from django.conf import settings

def add_logo(path):
    import cv2
    img = cv2.imread(path)
    cv2.putText(img=img, text=settings.AUTHOR_NAME, org=(50 * int(2 * (img.shape[1]/2000)), 50 * int(3 * (img.shape[1]/2000))), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=int(2 * (img.shape[1]/2000)), color=(255, 255, 255), thickness=4 * int(2 * (img.shape[1]/2000)))
    cv2.imwrite(path, img)
