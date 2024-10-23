import os
from django.conf import settings
from feed.models import Post, get_image_path
from django.urls import reverse

def tweet_photo():
    api_key = settings.TWITTER_KEY
    api_secrets = settings.TWITTER_SECRET
    access_token = settings.TWITTER_ACCESS_TOKEN
    access_secret = settings.TWITTER_TOKEN_SECRET
    import tweepy
    posts = Post.objects.filter(author__id=settings.MY_ID, enhanced=True, private=False, public=True, published=True, recipient=None).exclude(image=None, content="").order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=posts).order_by('?').first()
    auth = tweepy.OAuthHandler(api_key,api_secrets)
    auth.set_access_token(access_token,access_secret)
    api = tweepy.API(auth)
    api.verify_credentials()
#    full_path = os.path.join(settings.BASE_DIR, 'media/', get_image_path(post, 'image.png'))
#    with post.image_thumbnail_bucket.storage.open(str(post.image_thumbnail_bucket), mode='rb') as bucket_file:
#        with open(full_path, "wb") as image_file:
#            image_file.write(bucket_file.read())
#    media = api.media_upload(full_path)
    post_result = api.update_status('{} - {}{}'.format(post.content, settings.BASE_URL, reverse('feed:post-detail', kwargs={'uuid': post.uuid}))) #, media_ids=[media.media_id])
    os.remove(full_path)
