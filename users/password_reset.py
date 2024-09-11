from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

def send_password_reset_email(user):
    context = {
        "email": user.email,
        "domain": settings.DOMAIN,
        "site_name": settings.SITE_NAME,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        "token": default_token_generator.make_token(user),
        "protocol": "https"
    }
    to_email = user.email
    subject = loader.render_to_string("registration/password_reset_subject.txt", context)
    subject = "".join(subject.splitlines())
    body = loader.render_to_string("registration/password_reset_email.html", context)
    email_message = EmailMultiAlternatives(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    html_email = loader.render_to_string("registration/password_reset_email.html", context)
    email_message.attach_alternative(html_email, "text/html")
    email_message.send()
