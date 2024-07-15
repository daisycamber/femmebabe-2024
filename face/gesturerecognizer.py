from cvzone.HandTrackingModule import HandDetector
import cv2

detector = HandDetector(detectionCon=0.5, maxHands=100)

def validate_gesture(image_path):
    img = cv2.imread(image_path)
    hands, img = detector.findHands(img)
    if hands and len(hands) > 0:
        return True
    return False
