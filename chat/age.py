def readb64(uri):
    import numpy as np
    import cv2, base64
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

FAST_SCALE = 0.4

def resize_img(image):
    import cv2
    # Define the scale factor
    scale = FAST_SCALE
    # Calculate the new dimensions
    width = int(image.shape[1] * scale)
    height = int(image.shape[0] * scale)
    # Resize the image
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def is_nude(base64_data):
    img = resize_img(readb64(base64_data))
    import cv2
    from PIL import Image
    img_pil = Image.fromarray(img)
    import nude
    return nude.is_nude(img_pil)

def get_age(base64_data):
    from deepface import DeepFace
    img = resize_img(readb64(base64_data))
    result = DeepFace.analyze(img, actions=['age'])
    print(result)
    high = 0
    for obj in result:
        if 'age' in obj and obj['age']:
            if obj['age'] > high: high = obj['age']
    if len(result) > 0: return high
    return '?'

def verify_emotion(face_path):
    from deepface import DeepFace
    obj = DeepFace.analyze(img_path=face_path, actions=['gender','emotion'])[0]
    print(obj)
    if obj["emotion"]["happy"] > PEAK_HAPPY or obj["emotion"]["fear"] > PEAK_FEAR or obj["dominant_emotion"] == "happy":
        return False
    return True

def get_sex(base64_data):
    from deepface import DeepFace
    img = resize_img(readb64(base64_data))
    obj = DeepFace.analyze(img, actions=['gender'])
    print(obj)
    if len(obj) > 0 and 'gender' in obj[0] and obj[0]['gender']:
        return int(obj[0]['gender']['Woman'])
    return '?'

def is_violent(base64_data):
    from security.violence import detect
    img = resize_img(readb64(base64_data))
    return detect(img)
