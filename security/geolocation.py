import requests, json
from django.conf import settings

def get_ip_location(ip):
    response = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey={}&ip={}'.format(settings.GEOLOCATION_API_KEY, ip))
    print(response)
    result = response.json()
    try:
        return (float(result['latitude']), float(result['longitude']))
    except:
        return (None, None)
