import requests
import json

params = {
  'workflow': 'wfl_c6O5v2HL7wL8g6sWVpPnr',
  'api_user': '601803718',
  'api_secret': 'SZGfrk3gPkmby8G8is8E'
}

def is_allowable_face(face_path):
    try:
        files = {'media': open(face_path, 'rb')}
        r = requests.post('https://api.sightengine.com/1.0/check-workflow.json', files=files, data=params)
        output = json.loads(r.text)
    except:
        return False

    if output['status'] == 'failure' or output['summary']['action'] == 'reject':
        print(output)
        return False
    return True
