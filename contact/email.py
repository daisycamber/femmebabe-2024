from users.email import send_html_email
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User

def send_contact_confirmation(user, contact):
    subject = '[{}] Your message has been received.'.format(settings.SITE_NAME)
    message = render_to_string('contact/email.html', {
        'the_site_name': settings.SITE_NAME,
        'model_name': User.objects.get(id=settings.MY_ID).profile.name,
        'user': user,
        'base_url': settings.BASE_URL,
        'name': contact.name if contact.name else None,
        'contact': contact
    })
    send_html_email(user, subject, message)
