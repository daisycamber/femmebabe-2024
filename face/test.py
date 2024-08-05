import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from urllib.parse import urlparse
from io import BytesIO
# To install this module, run:
# python -m pip install Pillow
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, QualityForRecognition
import json

# This key will serve all examples in this document.
#KEY = "3a2ab4433c3146a9955457c353bdd7cd"
KEY = "ebebcce1a1d94e028fc34410eeb47cfe"

# This endpoint will be used in all examples in this quickstart.
ENDPOINT = "https://lotteh.cognitiveservices.azure.com/"

# Base url for the Verify and Facelist/Large Facelist operations
IMAGE_BASE_URL = 'https://csdx.blob.core.windows.net/resources/Face/Images/'

PERSON_GROUP_ID = str("lotteh-group") # assign a random ID (or name it anything)

def get_face_id(single_face_image_url):
    # Create an authenticated FaceClient.
    face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))
    # Detect a face in an image that contains a single face
#    single_image_name = os.path.basename(single_face_image_url)
    # We use detection model 3 to get better performance.
    face_ids = []
    # We use detection model 3 to get better performance, recognition model 4 to support quality for recognition attribute.
    faces = face_client.face.detect_with_url(single_face_image_url, detection_model='detection_03', recognition_model='recognition_04') #, return_face_attributes=['qualityForRecognition'])

    face_client.person_group.create(person_group_id=PERSON_GROUP_ID, name=PERSON_GROUP_ID)

    # remove this line on error

    for face in faces:
        face_ids.append(face.face_id)
    results = None
    try:
        results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
    except:
        results = None
    if not results:
        p = face_client.person_group_person.create(PERSON_GROUP_ID, uuid.uuid4())
        face_client.person_group_person.add_face_from_url(PERSON_GROUP_ID, p.person_id, single_face_image_url)
        face_client.person_group.train(PERSON_GROUP_ID)
        while (True):
            training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
            print("Training status: {}.".format(training_status.status))
            print()
            if (training_status.status is TrainingStatusType.succeeded):
                break
            elif (training_status.status is TrainingStatusType.failed):
                sys.exit('Training the person group has failed.')
            time.sleep(5)
        results = face_client.face.identify(face_ids, PERSON_GROUP_ID)
    if results and len(results) > 0:
        res = json.loads(str(results[0].candidates[0]).replace('\'',"\""))['person_id']
        print(res)
        return res
    return False

f = 'https://lotteh.com/media/face/b387d75d-b401-405d-8b5b-fc46129e6057.png'
print(get_face_id(f))
