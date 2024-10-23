import requests
import json
from django.conf import settings

api_user = settings.SIGHTENGINE_USER
api_secret = settings.SIGHTENGINE_SECRET

params = {
  'workflow': 'wfl_c7IKUvqOfigoGLdGcFoUS',
  'api_user': api_user,
  'api_secret': api_secret
}

def is_safe(video_path):
    try:
        files = {'media': open(video_path, 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/video/check-workflow-sync.json', files=files, data=params)
        output = json.loads(r.text)
        if output['status'] == 'failure' or output['summary']['action'] == 'reject':
            return False
    except: return False
    return True
