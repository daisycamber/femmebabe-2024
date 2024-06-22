import os
from feed.models import Post
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from contact.forms import ContactForm
from django.utils import timezone

def generate_site():
    from feed.templatetags.app_filters import embedlinks, addhttpstodomains, highlightcode
    images = ''
    count = 0
    for post in Post.objects.filter(uploaded=True, public=True, offsite=True, posted=True, published=True, feed="private").exclude(image_bucket=None).order_by('-date_posted'):
        images = images + '<div id="div{}"><p>{}</p><img width="100%" height="auto" src="{}" id="img{}"></div>\n'.format(count, post.content.replace('\n', ' '), post.image_offsite, count)
        count = count + 1
    blog = ''
    for post in Post.objects.filter(public=True, posted=True, published=True, feed="news").order_by('-date_posted'):
        text = ''
        for obj in highlightcode(post.content):
            text = embedlinks(addhttpstodomains(obj['text'])) + ('<pre class="language-{}"><code>{}</code></pre>'.format(obj['lang'], obj['code']) if ('code' in obj) and ('lang' in obj) else '')
            blog = blog + text
        blog = blog + '<hr>'
        count = count + 1
    context = {
        'site_name': settings.STATIC_SITE_NAME,
        'static_url': settings.STATIC_SITE_URL,
        'base_url': settings.BASE_URL,
        'author_name': settings.AUTHOR_NAME,
        'images': images,
        'model_name': User.objects.get(id=settings.MY_ID).profile.name,
        'model': User.objects.get(id=settings.MY_ID),
        'my_profile': User.objects.get(id=settings.MY_ID).profile,
        'typical_response_time': settings.TYPICAL_RESPONSE_TIME_HOURS,
        'contact_form': ContactForm(),
        'blog': blog,
        'github_url': settings.GITHUB_URL,
        'base_domain': settings.DOMAIN,
        'year': timezone.now().strftime('%Y'),
    }
    index = render_to_string('web/index.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'index.html'), 'w') as file:
        file.write(index)
