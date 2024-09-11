EXCLUDED_LABELS = [
    # outdoor cases
#    'people walking on a street',
#    'buildings',
    'fight on a street',
    'fire on a street',
    'street violence',
#    'road',
#    'car crash',
#    'cars on a road',
#    'car parking area',
#    'cars',
    # indoor cases
#    'office environment',
#    'office corridor',
    'violence in office',
    'fire in office',
#    'people talking',
#    'people walking in office',
#    'person walking in office',
#    'group of people',
]

def detect(image):
    import sys
    sys.path.append('/home/team/lotteh/violence-detection/')
    from model import Model
    import cv2
    model = Model()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    label = model.predict(image=image)['label']
    if label != 'Unknown' and label in EXCLUDED_LABELS: return True
    return False
