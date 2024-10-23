overwrite = False
PRIV_POSTS = 24
import os
from feed.models import Post
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from contact.forms import ContactForm
from django.utils import timezone
from feed.templatetags.app_filters import shorttitle
from django.urls import reverse

def generate_site():
    global overwrite
    global priv_posts
    from feed.templatetags.app_filters import embedlinks, addhttpstodomains, highlightcode
    images = ''
    init_images = ''
    count = 0
    for post in Post.objects.filter(uploaded=True, public=True, posted=True, published=True, feed="private").exclude(image_bucket=None).order_by('-date_posted'):
        if post.image and post.image:
            if post.image and not post.image_offsite: post.copy_web()
            img_url = post.get_image_url() if post.image_offsite else post.get_web_url()
            if not img_url: img_url = post.image_bucket.url if post.image_bucket else post.author.profile.get_image_url
            count = count + 1
            if count < 11:
                init_images = init_images + '<div id="div{}">{}'.format(count, post.content) + ('<img width="100%" height="auto" src="{}" id="img{}" alt="{}"/>'.format(img_url, count, shorttitle(post.id)) if post.image else '')
                init_images = init_images + '<p>{} | {} | {}</p></div><hr>\n'.format('<a href="/{}" title="{}">View</a>'.format(post.friendly_name, 'View Post - {} by {}'.format(shorttitle(post.id), post.author.profile.name)), '<a href="{}" title="{}">Buy</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-card', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid), 'Buy on {}'.format(settings.SITE_NAME)), '<a href="{}" title="{}">Buy with crypto</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-crypto', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid) + '&crypto={}'.format(settings.DEFAULT_CRYPTO), 'Buy with cryptocurrency on {}'.format(settings.SITE_NAME)))
                if count % 5 == 0:
                    init_images = init_images + render_to_string('banner_ad.html', {'show_ads': True}) + '<hr>'
            else:
                images = images + '<div id="div{}">{}'.format(count, post.content) + ('<img width="100%" height="auto" src="{}" id="img{}" alt="{}"/>'.format(img_url, count, shorttitle(post.id)) if post.image else '')
                images = images + '<p>{} | {} | {}</p></div><hr>\n'.format('<a href="/{}" title="{}">View</a>'.format(post.friendly_name, 'View Post - {} by {}'.format(shorttitle(post.id), post.author.profile.name)), '<a href="{}" title="{}">Buy</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-card', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid), 'Buy on {}'.format(settings.SITE_NAME)), '<a href="{}" title="{}">Buy with crypto</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-crypto', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid) + '&crypto={}'.format(settings.DEFAULT_CRYPTO), 'Buy with cryptocurrency on {}'.format(settings.SITE_NAME)))
    blog = ''
    for post in Post.objects.filter(public=True, posted=True, published=True, feed="blog").order_by('-date_posted'):
        text = ''
        title = shorttitle(post.id)
        print(post.content)
#        for obj in highlightcode(post.content):
#            text = embedlinks(addhttpstodomains(obj['text'])) + ('<pre class="language-{}"><code>{}</code></pre>'.format(obj['lang'], obj['code']) if ('code' in obj) and ('lang' in obj) else '')
#            blog = blog + text
        if not post.content_compiled:
            from feed.compile import compile
            compile(post)
            post = Post.objects.get(id=post.id)
        if post.image and not post.image_offsite: post.copy_web()
        img_url = post.get_image_url() if post.image_offsite else post.get_web_url()
        if not img_url: img_url = post.image_bucket.url if post.image_bucket else post.author.profile.get_image_url()
        blog = blog + '<div id="feed{}">{}'.format(count, post.content_compiled) + ('<img width="100%" height="auto" src="{}" id="img{}" alt="{}"/>'.format(img_url, count, title) if post.image else '')
        blog = blog + '<p>{} | {} | {}</p></div><hr>\n'.format('<a href="/{}" title="{}">View</a>'.format(post.friendly_name, 'View Post - {} by {}'.format(title, post.author.profile.name)), '<a href="{}" title="{}">Buy</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-card', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid), 'Buy on {}'.format(settings.SITE_NAME)), '<a href="{}" title="{}">Buy with crypto</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-crypto', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid) + '&crypto={}'.format(settings.DEFAULT_CRYPTO), 'Buy with cryptocurrency on {}'.format(settings.SITE_NAME)))
        count = count + 1
        if count%5 == 0:
            blog = blog + render_to_string('banner_ad.html', {'show_ads': True})
            blog = blog + '<hr>'
    context = {
        'site_name': settings.STATIC_SITE_NAME,
        'the_site_name': settings.STATIC_SITE_NAME,
        'static_url': settings.STATIC_SITE_URL,
        'site_url': settings.BASE_URL,
        'dedscription': settings.BASE_DESCRIPTION,
        'base_url': settings.STATIC_SITE_URL,
        'add_url': settings.ADD_URL,
        'author_name': settings.AUTHOR_NAME,
        'images': images,
        'init_images': init_images,
        'model_name': User.objects.get(id=settings.MY_ID).profile.name,
        'model': User.objects.get(id=settings.MY_ID),
        'my_profile': User.objects.get(id=settings.MY_ID).profile,
        'typical_response_time': settings.TYPICAL_RESPONSE_TIME_HOURS,
        'contact_form': ContactForm(),
        'blog': blog,
        'github_url': settings.GITHUB_URL,
        'base_domain': settings.DOMAIN,
        'base_description': settings.BASE_DESCRIPTION,
        'clock_color': '#ffcccb',
        'year': timezone.now().strftime('%Y'),
        'show_ads': True,
        'path': '/',
        'request': {},
        'footer': True
    }
    index = render_to_string('web/index.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'index.html'), 'w') as file:
        file.write(index)
    news = render_to_string('web/news.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'news.html'), 'w') as file:
        file.write(news)
    contact = render_to_string('web/contact.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'contact.html'), 'w') as file:
        file.write(contact)
    landing = render_to_string('web/landing.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'landing.html'), 'w') as file:
        file.write(landing)
    import urllib.parse
    from security.crypto import encrypt
    images = ''
    count = 0
    for post in Post.objects.filter(uploaded=True, private=True, posted=True, published=True, feed="private").exclude(image_bucket=None).order_by('-date_posted')[:PRIV_POSTS]:
        if post.image and post.image:
            if post.image and not post.image_offsite: post.copy_web()
            img_url = post.get_image_url() if post.image_offsite else post.get_web_url()
            if not img_url: img_url = post.image_bucket.url if post.image_bucket else post.author.profile.get_image_url
            count = count + 1
            images = images + '<div id="div{}">{}'.format(count, post.content) + ('<img width="100%" height="auto" src="{}" id="img{}" alt="{}"/>'.format(img_url, count, shorttitle(post.id)) if post.image else '')
            images = images + '<p>{} | {}</p></div><hr>\n'.format('<a href="{}/{}" title="{}">View</a>'.format(settings.BASE_URL, post.friendly_name, 'View Post - {} by {}'.format(shorttitle(post.id), post.author.profile.name)), '<a href="{}" title="{}">Buy with crypto</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-crypto', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid) + '&crypto={}'.format(settings.DEFAULT_CRYPTO), 'Buy with cryptocurrency on {}'.format(settings.SITE_NAME)))
    context['images'] = urllib.parse.quote(encrypt(images, settings.PRV_AES_KEY))
    private = render_to_string('web/private.html', context)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'private.html'), 'w') as file:
        file.write(private)
    urls = ['/', '/news', '/landing','/private','/index','/contact']
    context['footer'] = False
    for post in Post.objects.filter(public=True, posted=True, published=True, feed="blog").union(Post.objects.filter(uploaded=True, public=True, offsite=True, posted=True, published=True, feed="private").exclude(image_bucket=None)).order_by('-date_posted'):
        url = '/{}'.format(post.friendly_name)
        context['post'] = post
        context['path'] = url
        print(url)
        context['title'] = shorttitle(post.id)
        context['post_links'] = '<p>{} | {}</p>\n'.format('<a href="{}" title="{}">Buy</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-card', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid), 'Buy on {}'.format(settings.SITE_NAME)), '<a href="{}" title="{}">Buy with crypto</a>'.format(settings.BASE_URL + reverse('payments:buy-photo-crypto', kwargs={'username': post.author.profile.name}) + '?id={}'.format(post.uuid) + '&crypto={}'.format(settings.DEFAULT_CRYPTO), 'Buy with cryptocurrency on {}'.format(settings.SITE_NAME)))
        path = os.path.join(settings.BASE_DIR, 'web/site/', '{}.html'.format(post.friendly_name))
        if (not os.path.exists(path)) or overwrite:
            index = render_to_string('web/post.html', context)
            with open(path, 'w') as file:
                file.write(index)
        urls = urls + [url]
    context['path'] = '/404'
    context['title'] = 'Error 404 - File Not Found'
    path = os.path.join(settings.BASE_DIR, 'web/site/', '{}.html'.format('404'))
    if not os.path.exists(path) or overwrite:
        index = render_to_string('web/404.html', context)
        with open(path, 'w') as file:
            file.write(index)
    urls = urls + [url]
    sitemapcontext = {'base_url': settings.STATIC_SITE_URL, 'languages': ['en',], 'urls': urls, 'date': timezone.now().strftime('%Y-%m-%d')}
    index = render_to_string('web/sitemap.xml', sitemapcontext)
    with open(os.path.join(settings.BASE_DIR, 'web/site/', 'sitemap.xml'), 'w') as file:
        file.write(index)
