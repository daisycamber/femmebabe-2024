import requests
import json
from django.conf import settings

api_user = settings.SIGHTENGINE_USER
api_secret = settings.SIGHTENGINE_SECRET

def is_safe(image_path):
    params = {
        'workflow': 'wfl_c6O5v2HL7wL8g6sWVpPnr',
        'api_user': api_user,
        'api_secret': api_secret
    }
    files = {'media': open(image_path, 'rb')}
    r = requests.post('https://api.sightengine.com/1.0/check-workflow.json', files=files, data=params)
    output = json.loads(r.text)
    if output['status'] == 'failure' or output['summary']['action'] == 'reject':
        return False
    return True
