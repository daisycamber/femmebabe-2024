def send_photo_email(user, post):
    from users.email import send_html_email
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    from django.conf import settings
    from django.template.loader import render_to_string
    from feed.models import Post

    photo_url = post.get_image_url()
    html_message = render_to_string('feed/photo_email.html', {
        'site_name': settings.SITE_NAME,
        'user': user,
        'domain': settings.DOMAIN,
        'protocol': 'https',
        'photo': photo_url,
    })
    if not post.file or not os.path.exists(post.file.path): post.download_file()
    att = [post.file.path]
    send_html_email(user, 'Your Photo From  {}, {}'.format(settings.SITE_NAME, user.username), html_message, attachmments=att)
