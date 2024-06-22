from allauth.socialaccount.models import SocialLogin, SocialToken, SocialApp
#pip install pillar-youtube-upload
from google.oauth2.credentials import Credentials

def upload_youtube(user, file_path, title, description, tags, category='22', privacy_status='public', thumbnail=None):
#    social_token = SocialToken.objects.get(account__user__email=user.email, provider='google')
#    creds = Credentials(token=social_token.token,
#                    refresh_token=social_token.token_secret,
#                    client_id=social_token.app.client_id,
#                    client_secret=social_token.app.secret)
    from youtube_upload.client import YoutubeUploader
    uploader = YoutubeUploader()
#    uploader.authenticate(access_token=creds.token, refresh_token=creds.token_secret)
    uploader.authenticate(access_token=user.profile.token, refresh_token=user.profile.refresh_token)
    # Video options
    options = {
        "title" : title,
        "description" : description,
        "tags" : tags,
        "categoryId" : category,
        "privacyStatus" : privacy_status,
        "kids" : False,
        "thumbnailLink" : thumbnail
    }
    # upload video
    uploader.upload(file_path, options)
    return True
