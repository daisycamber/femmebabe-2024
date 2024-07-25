import google.oauth2.credentials
import google_auth_oauthlib.flow
from django.conf import settings
from django.urls import reverse
import os

def get_auth_url(email, passthrough_value):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(str(os.path.join(settings.BASE_DIR, 'client_secret.json')),
    scopes=['https://www.googleapis.com/auth/youtube.force-ssl',
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
    ])
    flow.redirect_uri = settings.BASE_URL + reverse('users:oauth')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=passthrough_value,
        login_hint=email,
        prompt='consent')
    return authorization_url

def parse_callback_url(authorization_response):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(str(os.path.join(settings.BASE_DIR, 'client_secret.json')),
    scopes=['https://www.googleapis.com/auth/youtube.force-ssl',
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
    ])
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    return credentials.token, credentials.refresh_token
