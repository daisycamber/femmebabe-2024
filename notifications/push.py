def routine_push():
    from pwa_webpush import send_group_notification
    from feed.models import Post
    from django.conf import settings
    posts = Post.objects.filter(author__id=settings.MY_ID, enhanced=True, private=False, public=True, published=True, recipient=None).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=posts).order_by('?').first()
    payload = {
        'head': 'See more on {}'.format(settings.SITE_NAME),
        'body': 'Visit {} today and see more posts like this one. I\'d love to see you there!'.format(settings.SITE_NAME),
        'icon': post.get_face_blur_thumb_url(),
        'url': settings.BASE_URL,
    }
    send_group_notification(group_name='guests', payload=payload)
