from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from face.tests import is_superuser_or_vendor
from feed.tests import identity_verified
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

def send_contact_push(name):
    from django.shortcuts import render
    from .models import Contact
    from .forms import ContactForm
    from django.shortcuts import get_object_or_404, render, redirect
    from django.urls import reverse
    from django.contrib import messages
    from django.http import HttpResponse
    from django.conf import settings
    from django.core.paginator import Paginator
    import traceback
    from django.contrib.auth.models import User
    from users.email import send_verification_email
    from users.models import Profile
    from security.models import SecurityProfile
    from users.username_generator import generate_username as get_random_username
    from django.utils.crypto import get_random_string
    from contact.email import send_contact_confirmation
    from security.apis import get_client_ip
    from security.apis import check_raw_ip_risk
    from django.conf import settings
    from pwa_webpush import send_user_notification
    payload = {
        'head': 'New contact on {}'.format(settings.SITE_NAME),
        'body': 'Meet the new contact, "{}", on {}'.format(name, settings.SITE_NAME),
        'icon': settings.BASE_URL + settings.ICON_URL,
        'url': settings.BASE_URL + reverse('contact:contacts'),
    }
    try:
        send_user_notification(User.objects.get(id=settings.MY_ID), payload=payload)
    except: pass #print(traceback.format_exc())

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_superuser_or_vendor)
def contacts(request):
    from django.shortcuts import render
    from .models import Contact
    from .forms import ContactForm
    from django.shortcuts import get_object_or_404, render, redirect
    from django.urls import reverse
    from django.contrib import messages
    from django.http import HttpResponse
    from django.conf import settings
    from django.core.paginator import Paginator
    import traceback
    from django.contrib.auth.models import User
    from users.email import send_verification_email
    from users.models import Profile
    from security.models import SecurityProfile
    from users.username_generator import generate_username as get_random_username
    from django.utils.crypto import get_random_string
    from contact.email import send_contact_confirmation
    from security.apis import get_client_ip
    from security.apis import check_raw_ip_risk
    from django.conf import settings
    page = 1
    if(request.GET.get('page', None) != None):
        page = int(request.GET.get('page', 1))
    c = Contact.objects.all().order_by('-date_sent')
    p = Paginator(c, 20)
    if page > p.num_pages or page < 1:
        messages.warning(request, "The page you requested, " + str(page) + ", does not exist. You have been redirected to the first page.")
        page = 1
    return render(request, 'contact/contacts.html', {'title': 'Contacts', 'contacts': p.page(page), 'page_obj': p.get_page(page), 'page': page, 'count': p.count})

@csrf_exempt
def contact(request):
    from django.shortcuts import render
    from .models import Contact
    from .forms import ContactForm
    from django.shortcuts import get_object_or_404, render, redirect
    from django.urls import reverse
    from django.contrib import messages
    from django.http import HttpResponse
    from django.conf import settings
    from django.core.paginator import Paginator
    import traceback
    from django.contrib.auth.models import User
    from users.email import send_verification_email
    from users.models import Profile
    from security.models import SecurityProfile
    from users.username_generator import generate_username as get_random_username
    from django.utils.crypto import get_random_string
    from contact.email import send_contact_confirmation
    from security.apis import get_client_ip
    from security.apis import check_raw_ip_risk
    from django.conf import settings
    from users.email import sendwelcomeemail
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ip = get_client_ip(request)
            form.instance.ip = ip
            contact = form.save()
            e = contact.email
            from email_validator import validate_email
            valid = validate_email(e, check_deliverability=True)
            us = User.objects.filter(email=e).last()
            safe = not check_raw_ip_risk(ip, soft=True, dummy=False, guard=True)
            if valid and (not us) and safe:
                user = User.objects.create_user(email=e, username=get_random_username(), password=get_random_string(length=8))
                if not hasattr(user, 'profile'):
                    profile = Profile.objects.create(user=user)
                    profile.finished_signup = False
                    profile.save()
                    security_profile = SecurityProfile.objects.create(user=user)
                    security_profile.save()
                send_verification_email(user)
                sendwelcomeemail(user)
            elif not valid: HttpResponse('Invalid or undeliverable email, please check the email and try again')
            elif not safe: HttpResponse('You are using a risky IP address, and your contact request has been denied.')
            us = User.objects.filter(email=e).last()
            contact.user = us
            contact.save()
            send_contact_confirmation(us, contact)
            send_contact_push(contact.name)
            return HttpResponse('Message sent.')
        else: return HttpResponse(str(form.errors))
    return redirect(reverse('/'))

