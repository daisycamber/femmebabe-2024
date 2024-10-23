import os
import requests
import json
from .nude import is_nude
from face.deep import is_face, verify_age
from django.conf import settings
from feed.middleware import get_current_user
from feed.audiotovideo import audio_to_video

api_user = settings.SIGHTENGINE_USER
api_secret = settings.SIGHTENGINE_SECRET


def sightengine_image(image_path):
    params = {
        'workflow': 'wfl_chz5r9ffPSio8qWGRryUf',
        'api_user': api_user,
        'api_secret': api_secret
    }
    files = {'media': open(image_path, 'rb')}
    r = requests.post('https://api.sightengine.com/1.0/check-workflow.json', files=files, data=params)
    return r.text

base_path = os.path.join(settings.BASE_DIR, 'temp/')

def sightengine_audio(file_path):
    op = ''
    try:
        image = get_current_user().profile.image.path
        output = os.path.join(base_path, get_current_user().profile.name + '.mp4')
        audio_to_video(file_path, image, output)
        op = sightengine_file(output)
        os.remove(output)
    except: pass
    return op

def sightengine_file(file_path):
    params = {
        'workflow': 'wfl_chz7AZ2mLuIfzDhgPOKwM',
        'api_user': api_user,
        'api_secret': api_secret
    }
    files = {'media': open(file_path, 'rb')}
    r = requests.post('https://api.sightengine.com/1.0/video/check-workflow-sync.json', files=files, data=params)
    return r.text

def is_safe_public_video(video_path):
    params = {
        'workflow': 'wfl_caKQzh2jI3i0gPINGCLZf',
        'api_user': api_user,
        'api_secret': api_secret
    }
    try:
        files = {'media': open(video_path, 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/video/check-workflow-sync.json', files=files, data=params)
        output = json.loads(r.text)
        if output['status'] == 'failure' or output['summary']['action'] == 'reject':
            return False
    except: return False
    return True

def is_safe_private_video(video_path):
    params = {
        'workflow': 'wfl_c7IKUvqOfigoGLdGcFoUS',
        'api_user': api_user,
        'api_secret': api_secret
    }
    try:
        files = {'media': open(video_path, 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/video/check-workflow-sync.json', files=files, data=params)
        output = json.loads(r.text)
        if output['status'] == 'failure' or output['summary']['action'] == 'reject':
            return False
    except: return False
    return True


def is_safe_public_image(image_path):
    try:
        if is_nude(image_path):
            return False
        if is_face(image_path) and not verify_age(image_path):
            return False
        params = {
            'workflow': 'wfl_caKzFYrxZceA446e4oc4W',
            'api_user': api_user,
            'api_secret': api_secret
        }
        files = {'media': open(image_path, 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/check-workflow.json', files=files, data=params)
        output = json.loads(r.text)
        if output['status'] == 'failure' or output['summary']['action'] == 'reject':
            print(output)
            return False
    except: return False
    return True

def is_safe_private_image(image_path):
    try:
        if is_face(image_path) and not verify_age(image_path):
            return False
        params = {
            'workflow': 'wfl_caKGh5Hee1rQM9rjWlSBv',
            'api_user': api_user,
            'api_secret': api_secret
        }
        files = {'media': open(image_path, 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/check-workflow.json', files=files, data=params)
        output = json.loads(r.text)
        if output['status'] == 'failure' or output['summary']['action'] == 'reject':
            print(output)
            return False
    except: return False
    return True
