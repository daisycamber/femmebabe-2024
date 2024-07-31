from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified, identity_really_verified
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import patch_cache_control
from django.views.decorators.vary import vary_on_cookie

def render_agreement(name, parent, mother):
    from django.conf import settings
    from django.utils import timezone
    from django.template.loader import render_to_string
    from feed.templatetags.nts import nts
    return render_to_string('payments/surrogacy.txt', {
        'the_clinic_name': settings.FERTILITY_CLINIC,
        'the_site_name': settings.SITE_NAME,
        'mother_name': name,
        'mother_address': mother.vendor_profile.address,
        'mother_insurance': mother.vendor_profile.insurance_provider,
        'the_state_name': 'Washington',
        'parent_name': parent.verifications.last().full_name if parent and parent.verifications.last() else '________________',
        'surrogacy_fee': nts(settings.SURROGACY_FEE),
        'business_type': settings.BUSINESS_TYPE,
        'the_date': timezone.now().strftime('%B %d, %Y'),
    })

@cache_page(60*60*24*365)
def cancel(request):
    from django.shortcuts import render
    from contact.forms import ContactForm
    r = render(request, 'payments/cancel_payment.html', {'title':'We\'re sad to see you go', 'contact_form': ContactForm()})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

@cache_page(60*60*24*365)
def success(request):
    from django.shortcuts import render
    r = render(request, 'payments/success.html', {'title': 'Thank you for your payment'})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

@cache_page(60*60*24*365)
def webdev(request):
    from django.shortcuts import render
    from django.conf import settings
    from payments.stripe import WEBDEV_DESCRIPTIONS
    prices = ['100', '200', '500', '1000', '2000', '5000']
    price_dev = []
    for x in range(0, len(prices)):
        price_dev = price_dev + [{'price': prices[x], 'description': WEBDEV_DESCRIPTIONS[x]}]
    from contact.forms import ContactForm
    r = render(request, 'payments/webdev.html', {'title': 'Web Development Pricing', 'plans': price_dev, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'email_query_delay': 30, 'contact_form': ContactForm()})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r


@cache_page(60*60*24*365)
def idscan(request):
    from django.conf import settings
    from django.shortcuts import render
    price_scans = ['5','10', '20', '50', '100', '200', '500', '1000', '2000', '5000']
    r = render(request, 'payments/idscan.html', {'title': 'ID Scanner Pricing', 'plans': price_scans, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'email_query_delay': 30, 'free_trial': settings.IDSCAN_TRIAL_DAYS})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

@cache_page(60*60*24*365)
def surrogacy(request, username):
    from django.conf import settings
    from django.shortcuts import render
    from django.contrib.auth.models import User
    from feed.models import Post
    vendor = User.objects.get(profile__name=username, profile__vendor=True)
    agreement = render_agreement(vendor.profile.name if not vendor.verifications.last() else vendor.verifications.last().full_name, request.user.verifications.last().full_name if request.user.is_authenticated and request.user.verifications.last() else None, vendor)
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    r = render(request, 'payments/surrogacy.html', {'title': 'Surrogacy Plans', 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'post': post, 'vendor': vendor, 'agreement': agreement, 'surrogacy_fee': settings.SURROGACY_FEE, 'business_type': settings.BUSINESS_TYPE,})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

@cache_page(60*60*24*7)
def surrogacy_info(request, username):
    from django.conf import settings
    from django.shortcuts import render
    from django.contrib.auth.models import User
    from feed.models import Post
    from contact.forms import ContactForm
    vendor = User.objects.get(profile__name=username, profile__vendor=True)
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    r = render(request, 'payments/surrogacy_info.html', {'title': 'Surrogacy Plan Information', 'post': post, 'vendor': vendor, 'surrogacy_fee': settings.SURROGACY_FEE, 'contact_form': ContactForm()})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r


@login_required
@user_passes_test(identity_really_verified, login_url='/verify/', redirect_field_name='next')
def connect_account(request):
    from django.shortcuts import redirect
    from .stripe import create_connected_account
    return redirect(create_connected_account(request.user.id))

@login_required
def model_subscription_cancel(request, username):
    import stripe
    from django.contrib.auth.models import User
    from payments.models import Subscription
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.urls import reverse
    vendor = User.objects.get(profile__name=username, profile__vendor=True)
    for sub in Subscription.objects.filter(user=request.user, model=vendor, active=True):
        stripe.Subscription.delete(sub.stripe_subscription_id)
        sub.active = False
        sub.save()
        messages.success(request, 'You have cancelled your subscription. Please consider another plan.')
    return redirect(reverse('app:app'))

@login_required
def subscription_cancel(request):
    import stripe
    from django.urls import reverse
    from django.shortcuts import redirect
    from django.contrib import messages
    if request.user.profile.idscan_active:
        stripe.Subscription.delete(request.user.profile.stripe_subscription_id)
        request.user.profile.idscan_active = False
        request.user.profile.save()
        request.user.save()
        messages.success(request, 'You have cancelled your subscription. Please consider another plan.')
    return redirect(reverse('payments:idscan'))

@login_required
def webdev_subscription_cancel(request):
    import stripe
    from django.contrib import messages
    from django.shortcuts import redirect
    from django.urls import reverse
    if request.user.profile.webdev_active:
        stripe.Subscription.delete(request.user.profile.stripe_subscription_service_id)
        request.user.profile.webdev_active = False
        request.user.profile.save()
        request.user.save()
        messages.success(request, 'You have cancelled your subscription. Please consider another plan.')
    return redirect(reverse('payments:webdev'))

@csrf_exempt
def webhook(request):
    payload = request.body
    event = None
    import stripe
    from django.conf import settings
    stripe.api_key = settings.STRIPE_API_KEY
    from payments.stripe import PRICE_IDS
    from payments.stripe import PROFILE_MEMBERSHIP_PRICE_IDS
    from payments.stripe import PHOTO_PRICE_IDS
    from payments.stripe import WEBDEV_PRICE_IDS
    from payments.stripe import WEBDEV_MONTHLY_PRICE_IDS
    from payments.stripe import WEBDEV_DESCRIPTIONS
    from payments.stripe import PROFILE_MEMBERSHIP
    from payments.stripe import PHOTO_PRICE
    from payments.models import Subscription, PurchasedProduct
    from users.models import Profile
    from security.models import SecurityProfile
    price_scans = ['5','10', '20', '50', '100', '200', '500', '1000', '2000', '5000']
    price_dev = ['100', '200', '500', '1000', '2000', '5000']
    try:
        import json
        event = stripe.Event.construct_from(
            json.loads(payload), settings.STRIPE_API_KEY
        )
    except ValueError as e:
        from django.http import HttpResponse
        return HttpResponse(status=400)
    session = event.data['object']
    account = None
    invoice = stripe.Invoice.retrieve(session.get('invoice'))
    account = invoice['transfer_data']['destination'] if invoice['transfer_data'] else None
    print(str(invoice))
    if event.type == 'checkout.session.completed' or event.type == 'charge.captured' or event.type == 'charge.succeeded' or event.type == 'customer.subscripton.resumed' or event.type == 'invoice.created' or event.type == 'invoice.paid':
#        print(str(session))
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get("subscription")
        stripe_price_id = None
        stripe_product_id = None
        line_items = stripe.checkout.Session.list_line_items(session.get('id'))['data'][0]
        try: stripe_price_id = line_items['price']['id']
        except: pass
        try: stripe_product_id = line_items['price']['product']
        except: pass
        print('price: {}, prod: {}'.format(stripe_price_id, stripe_product_id))
#        account = session.get("account")
        metadata = session.get("metadata")
        email = session.get('customer_details')['email'] if 'email' in session.get('customer_details').keys() else session.get('customer_email')
        print(email)
        from django.contrib.auth.models import User
        user = None if User.objects.filter(email=email).count() < 1 else User.objects.filter(email=email).order_by('-profile__last_seen').first()
        if not user:
            from django.utils.crypto import get_random_string
            from users.username_generator import generate_username
            user = User.objects.create_user(email=email, username=generate_username(), password=get_random_string(8))
            if not hasattr(user, 'profile'):
                from users.models import Profile
                from security.models import SecurityProfile
                profile = Profile.objects.create(user=user)
                profile.finished_signup = False
                profile.save()
                security_profile = SecurityProfile.objects.create(user=user)
                security_profile.save()
            client_reference_id = user.id
            user.profile.stripe_customer_id = stripe_customer_id
            if stripe_price_id in WEBDEV_MONTHLY_PRICE_IDS:
                user.profile.stripe_subscription_service_id = stripe_subscription_id
            else:
                user.profile.stripe_subscription_id = stripe_subscription_id
            user.profile.save()
            from users.email import send_verification_email
            from users.password_reset import send_password_reset_email
            send_verification_email(user)
            send_password_reset_email(user)
        else:
            user = None
            try: user = User.objects.get(id = client_reference_id)
            except: user = User.objects.filter(email=email).order_by('-profile__last_seen').first()
            user.profile.stripe_customer_id = stripe_customer_id,
            if stripe_price_id in WEBDEV_MONTHLY_PRICE_IDS:
                user.profile.stripe_subscription_service_id = stripe_subscription_id
            else:
                user.profile.stripe_subscription_id = stripe_subscription_id
            user.profile.save()
        print(user.username)
        print('Checking for idscan plan')
        try:
            plan = PRICE_IDS.index(stripe_price_id)
            user.profile.idscan_plan = int(price_scans[plan]) * 2
            user.profile.idscan_active = True
            user.profile.idscan_used = 0
            user.profile.save()
            user.save()
            from users.tfa import send_user_text
            send_user_text(User.objects.get(id=settings.MY_ID), '@{} has purchased an ID scanner subscription product for ${}'.format(user.username, price_scans[plan]))
        except:
            print('None found, checking for webdev')
            try:
                product = WEBDEV_PRICE_IDS.index(stripe_price_id)
                product_desc = WEBDEV_DESCRIPTIONS[product]
                from payments.models import PurchasedProduct
                from users.tfa import send_user_text
                PurchasedProduct.objects.create(user=user, description=product_desc, price=int(price_dev[product]), paid=True)
                send_user_text(User.objects.get(id=settings.MY_ID), '@{} has purchased a web dev product for ${} - "{}"'.format(user.username, price_dev[product], product_desc))
            except:
                print('Checking for profile membership')
                if account and stripe_product_id == PROFILE_MEMBERSHIP:
                    vendor = User.objects.get(profile__stripe_id=account)
                    user.profile.subscriptions.add(vendor)
                    user.profile.save()
                    from payments.models import Subscription
                    if not Subscription.objects.filter(model=vendor, user=user, active=True).last(): Subscription.objects.create(model=vendor, user=user, active=True, strip_subscription_id=stripe_subscription_id)
                elif account and stripe_product_id == PHOTO_PRICE:
                    vendor = User.objects.get(profile__stripe_id=account)
                    from feed.models import Post
                    post = Post.objects.get(author=vendor, id=int(metadata[0]))
                    if not post.paid_file:
                        post.recipient = user
                        post.save()
                        from feed.email import send_photo_email
                        send_photo_email(user, post)
                    else:
                        from feed.email import send_photo_email
                        send_photo_email(user, post)
                        post.paid_users.add(user)
                        post.save()
                else:
                    from .stripe import SURROGACY_PRICE_ID
                    if SURROGACY_PRICE_ID == stripe_price_id:
                        mother = User.objects.get(profile__stripe_id=account)
                        from users.tfa import send_user_text
                        send_user_text(mother, '{} (@{}) has purchased a surrogacy plan with you. Please update them with details.'.format(user.verifications.last().full_name, user.username))
                        from payments.surrogacy import save_and_send_agreement
                        save_and_send_agreement(mother, user)
                    else:
                        try:
                            product = WEBDEV_MONTHLY_PRICE_IDS.index(stripe_price_id)
                            if product != None:
                                user.profile.webdev_plan = int(price_dev[product])
                                user.profile.webdev_active = True
                                user.profile.save()
                                from payments.models import PurchasedProduct
                                PurchasedProduct.objects.create(user=user, description=product_desc, price=int(price_dev[product]), paid=True, monthly=True)
                                from users.tfa import send_user_text
                                send_user_text(User.objects.get(id=settings.MY_ID), '@{} has purchased a web dev product for ${} - "{}"'.format(user.username, price_dev[product], product_desc))
                        except: pass
    elif event.type == 'charge.failed' or event.type == 'charge.refunded' or event.type == 'customer.subscripton.deleted' or event.type == 'customer.subscripton.paused' or event.type == 'invoice.deleted':
        session = event.data['object']
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get("subscription")
        stripe_price_id = None
        stripe_product_id = None
        line_items = stripe.checkout.Session.list_line_items(session.get('id'))['data'][0]
        try: stripe_price_id = line_items['price']['id']
        except: pass
        try: stripe_product_id = line_items['price']['product']
        except: pass
        print('price: {}, prod: {}'.format(stripe_price_id, stripe_product_id))
        from django.contrib.auth.models import User
        try:
            plan = PRICE_IDS.index(stripe_price_id)
            user = User.objects.get(profile__stripe_customer_id=stripe_customer_id)
            user.profile.idscan_active = False
            user.profile.save()
            user.save()
        except:
            if stripe_product_id == PROFILE_MEMBERSHIP and account:
                vendor = User.objects.get(profile__stripe_id=account)
                user.profile.subscriptions.remove(vendor)
                user.profile.save()
    else:
        print('Unhandled event type {}'.format(event.type))
    from django.http import HttpResponse
    return HttpResponse(status=200)

@csrf_exempt
def monthly_checkout_profile(request):
    import stripe
    from django.contrib.auth.models import User
    from django.conf import settings
    from django.http import JsonResponse
    import random
    plan = int(request.GET.get('plan'))
    price_scans = [5, 10, 15, 20, 25, 50, 75, 100, 200, 500, 1000, 2000, 5000]
    id = price_scans.index(plan)
    from payments.stripe import PROFILE_MEMBERSHIP_PRICE_IDS
    from payments.stripe import PROFILE_MEMBERSHIP
    price = PROFILE_MEMBERSHIP_PRICE_IDS[0] # id
    vendor = User.objects.get(profile__stripe_id=request.GET.get('vendor', None))
    if request.method == "GET":
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else random.randint(111111,999999),
                success_url=domain_url + "/payments/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "/payments/cancel/",
                payment_method_types= ["card", "us_bank_account"],
                mode = "subscription",
                line_items=[
                    {
                        "price_data": {"currency": settings.CURRENCY, "unit_amount": plan * 100, "product": PROFILE_MEMBERSHIP, "recurring": {"interval": "month"}},
                        "quantity": 1
                    }
                ],
                allow_promotion_codes=True,
                subscription_data={
                    "trial_period_days": int(vendor.vendor_profile.free_trial),
                    "application_fee_percent": settings.APPLICATION_FEE,
                    "transfer_data": {"destination": request.GET.get('vendor', None)},
                } if request.GET.get('vendor', None) else None,
            )
            print(checkout_session)
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)})

@csrf_exempt
def monthly_checkout(request):
    import stripe
    from django.contrib.auth.models import User
    from django.conf import settings
    from django.http import JsonResponse
    import random
    plan = int(request.GET.get('plan'))
    price_scans = [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]
    id = price_scans.index(plan)
    from payments.stripe import PRICE_IDS
    price = PRICE_IDS[id]
    if request.method == "GET":
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else random.randint(111111,999999),
                success_url=domain_url + "/payments/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "/payments/cancel/",
                payment_method_types= ["card", "us_bank_account"],
                mode = "subscription",
                line_items=[
                    {
                        "price": price,
                        "quantity": 1
                    }
                ],
                allow_promotion_codes=True,
                subscription_data={
                    "trial_period_days": settings.IDSCAN_TRIAL_DAYS if id < 3 else 0,
                    "application_fee_percent": settings.APPLICATION_FEE,
                    "transfer_data": {"destination": request.GET.get('vendor', None)},
                } if False and request.GET.get('vendor', None) else None,
            )
            print(checkout_session)
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)})

@csrf_exempt
def onetime_checkout_photo(request):
    import stripe
    from django.contrib.auth.models import User
    from django.conf import settings
    from django.http import JsonResponse
    from feed.models import Post
    import random
    photo = request.GET.get('photo', None)
    vendor = Post.objects.filter(id=int(photo)).first().author
    if request.method == "GET":
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            from payments.stripe import PHOTO_PRICE
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else random.randint(111111,999999),
                success_url=domain_url + "/payments/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "/payments/cancel/",
                payment_method_types= ["card", "us_bank_account"],
                mode = "payment",
                line_items=[
                    {
                        "price_data": {"currency": settings.CURRENCY, "unit_amount": int(Post.objects.filter(id=str(photo)).first().price) * 100, "product": PHOTO_PRICE},
                        "quantity": 1
                    }
                ],
                metadata = [photo],
                allow_promotion_codes=True,
                payment_intent_data={
                    "application_fee_amount": settings.APPLICATION_FEE_PHOTO,
                    "transfer_data": {"destination": vendor.profile.stripe_id},
                },
            )
            print(checkout_session)
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)})

@csrf_exempt
def onetime_checkout(request):
    import stripe
    from django.contrib.auth.models import User
    from django.conf import settings
    from django.http import JsonResponse
    import random
    plan = int(request.GET.get('plan'))
    monthly = request.GET.get('monthly', False) != False
    price_scans = [100, 200, 500, 1000, 2000, 5000]
    id = price_scans.index(plan)
    from payments.stripe import WEBDEV_PRICE_IDS, WEBDEV_MONTHLY_PRICE_IDS
    price = WEBDEV_PRICE_IDS[id] if not monthly else WEBDEV_MONTHLY_PRICE_IDS[id]
    if request.method == "GET":
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else random.randint(111111,999999),
                success_url=domain_url + "/payments/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "/payments/cancel/",
                payment_method_types= ["card", "us_bank_account"],
                mode = "payment" if not monthly else "subscription",
                line_items=[
                    {
                        "price": price,
                        "quantity": 1
                    }
                ],
                allow_promotion_codes=True,
                payment_intent_data={
                    "application_fee_percent": settings.APPLICATION_FEE,
                    "transfer_data": {"destination": request.GET.get('vendor', None)},
                } if request.GET.get('vendor', None) else None,
            )
            print(checkout_session)
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)})

@csrf_exempt
def onetime_checkout_surrogacy(request):
    import stripe
    from django.contrib.auth.models import User
    from django.conf import settings
    from django.http import JsonResponse
    from payments.stripe import SURROGACY_PRICE_ID
    import random
    vendor = User.objects.get(id=int(request.GET.get('vendor', None)))
    price = SURROGACY_PRICE_ID
    if request.method == "GET":
        domain_url = settings.BASE_URL
        stripe.api_key = settings.STRIPE_API_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else random.randint(111111,999999),
                success_url=domain_url + "/payments/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "/payments/cancel/",
                payment_method_types= ["card", "us_bank_account"],
                mode = "payment",
                line_items=[
                    {
                        "price": price,
                        "quantity": 1
                    }
                ],
                allow_promotion_codes=True,
                payment_intent_data={
                    "application_fee_amount": settings.APPLICATION_FEE_SURROGACY,
                    "transfer_data": {"destination": vendor.profile.stripe_id},
                } if request.GET.get('vendor', None) else None,
            )
            print(checkout_session)
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            print(str(e))
            return JsonResponse({"error": str(e)})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def card_list(request):
    from .models import PaymentCard
    from django.shortcuts import render
    cards = PaymentCard.objects.filter(user=request.user).order_by('-primary')
    return render(request, 'payments/payment_cards.html', {'title': 'Payment Cards', 'cards': cards})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def card_primary(request, id):
    from django.http import HttpResponse
    from payments.models import PaymentCard
    card = PaymentCard.objects.filter(id=int(id)).first()
    if request.method == 'POST':
        from django.contrib import messages
        for c in PaymentCard.objects.filter(user=request.user):
            c.primary = False
            c.save()
        card.primary = True
        card.save()
        messages.success(request, 'The card ending in *{} is now your primary payment card.'.format(str(card.number)[12:]))
    return HttpResponse('<i class="bi bi-pin-angle-fill"></i>' if card.primary else '<i class="bi bi-pin-fill"></i>')

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def card_delete(request, id):
    from django.http import HttpResponse
    from payments.models import PaymentCard
    if request.method == 'POST':
        from django.contrib import messages
        card = PaymentCard.objects.filter(id=int(id)).first()
        messages.success(request, 'The card ending in *{} was deleted.'.format(str(card.number if card and card.number else '****************')[12:]))
        if card: card.delete()
    return HttpResponse('Deleted')


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def cancel_subscription(request, username):
    from django.contrib.auth.models import User
    from django.shortcuts import redirect
    from django.urls import reverse
    import stripe
    model = User.objects.get(profile__name=username, profile__vendor=True)
    if not model in request.user.profile.subscriptions.all():
        return redirect(reverse('feed:profile', kwargs={'username': model.profile.name}))
    fee = model.vendor_profile.subscription_fee
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_API_KEY
        stripe.Subscription.delete(sub.stripe_subscription_id)
        from payments.models import Subscription
        sub = Subscription.objects.filter(active=True, model=model, user=request.user).last()
        sub.active = False
        sub.save()
        request.user.profile.subscriptions.delete(remove)
        request.user.profile.save()
        from django.contrib import Messages
        messages.success(request, 'You have cancelled your subscription.')
        return redirect(reverse('feed:home'))
    from django.shortcuts import render
    return render(request, 'payments/cancel.html', {
        'title': 'Cancel Subscription',
        'model': model
    })

@cache_page(60*60*24*7)
def subscribe_card(request, username):
    from django.contrib.auth.models import User
    from feed.models import Post
    from django.shortcuts import redirect
    from django.urls import reverse
    user = User.objects.get(profile__name=username, profile__vendor=True)
    if hasattr(request, 'user') and request.user.is_authenticated and user in request.user.profile.subscriptions.all():
        return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
    profile = user.profile
    fee = user.vendor_profile.subscription_fee
    from django.conf import settings
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    from django.shortcuts import render
    r = render(request, 'payments/subscribe_card.html', {'title': 'Subscribe', 'username': username, 'profile': profile, 'fee': fee, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'model': user.profile, 'post': post})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip_card(request, username, tip):
    from django.contrib.auth.models import User
    from .forms import CardNumberForm, CardInfoForm
    from .models import PaymentCard, CardPayment
    from django.contrib import messages
    fee = tip
    user = User.objects.get(profile__name=username, profile__vendor=True)
    profile = user.profile
    if request.method == 'POST':
        num_form = CardNumberForm(request.user,request.POST)
        card = None
        if num_form.is_valid():
            if PaymentCard.objects.filter(user=request.user, number=num_form.cleaned_data.get('number')).count() > 0: card = PaymentCard.objects.filter(user=request.user, number=num_form.cleaned_data.get('number')).last()
            else: card = num_form.save()
        else:
            messages.warning(request, num_form.errors)
        info_form = CardInfoForm(request.user, request.POST, instance=card)
        if info_form.is_valid():
            if info_form.cleaned_data.get('expiry_year') < 2000:
                info_form.instance.expiry_year = info_form.cleaned_data.get('expiry_year') - 2000
            card = info_form.save()
        else:
            messages.warning(request, info_form.errors)
            card.delete()
            card = None
        if card:
#            from payments.authorizenet import pay_fee
#            if pay_fee(user, fee, card, name='Tip to {}\'s profile'.format(user.profile.name), description='One time tip for adult webcam modeling content.'):
            if False:
                CardPayment.objects.create(user=request.user, amount=fee)
                from users.tfa import send_user_text
                send_user_text(user, '{} has tipped you ${}, {}.'.format(request.user.profile.name, fee, user.profile.preferred_name))
                messages.success(request, 'Your payment was processed. Thank you for the tip!')
                from django.shortcuts import redirect
                from django.urls import reverse
                return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
            else:
                messages.warning(request, 'Your payment wasn\'t processed successfully. Please try a new form of payment.')
    from django.shortcuts import render
    r = render(request, 'payments/tip_card.html', {'title': 'Tip With Credit or Debit Card', 'username': username, 'profile': profile, 'card_info_form': CardInfoForm(request.user), 'card_number_form': CardNumberForm(request.user, initial={'address': request.user.verifications.last().address if request.user.verifications.last() else ''}), 'fee': fee, 'username': username, 'profile': profile, 'usd_fee': fee})
    return r


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def subscribe_bitcoin_thankyou(request, username):
    from django.contrib.auth.models import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    if user in request.user.profile.subscriptions.all():
        from django.contrib import messages
        messages.success(request, 'Your payment has been verified. Thank you for subscribing! - {}'.format(user.profile.name))
        from django.shortcuts import redirect
        from django.urls import reverse
        return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
    from django.shortcuts import render
    return render(request, 'payments/subscribe_bitcoin_thankyou.html', {'title': 'Thanks - {}', 'profile': user.profile})

#@login_required
#@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def subscribe_bitcoin(request, username):
    from django.shortcuts import redirect
    from django.conf import settings
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto') if request.GET.get('crypto') else 'BTC'
    from django.contrib.auth.models import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    from django.contrib import messages
    from django.urls import reverse
    if request.user.is_authenticated and user in request.user.profile.subscriptions.all():
        return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
    from payments.models import VendorPaymentsProfile
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    usd_fee = user.vendor_profile.subscription_fee
    from .forms import BitcoinPaymentForm, BitcoinPaymentFormUser
    if request.method == 'POST':
        form = BitcoinPaymentForm(request.POST) if request.user.is_authenticated else BitcoinPaymentFormUser(request.POST)
        if form.is_valid():
            messages.success(request, 'We are validating your crypto payment. Please allow up to 15 minutes for this process to take place.')
            cus_user = User.objects.filter(profile__email=form.cleaned_data.get('email', None)).order_by('-last_seen')[0] if not request.user.is_authenticated else request.user
            if not (cus_user and cus_user.email != '' and cus_user.email != None):
                cus_user = None
                from email_validator import validate_email
                e = form.cleaned_data.get('email', None)
                if e:
                    try:
                        from security.apis import check_raw_ip_risk
                        from security.models import SecurityProfile
                        from users.models import Profile
                        from users.email import send_verification_email, sendwelcomeemail
                        from users.views import send_registration_push
                        valid = validate_email(e, check_deliverability=True)
                        us = User.objects.filter(email=e).last()
                        safe = not check_raw_ip_risk(ip, soft=True, dummy=False, guard=True)
                        if valid and not us and safe:
                            cus_user = User.objects.create(email=e, username=get_random_username(), password=get_random_string(length=8))
                            if not hasattr(cus_user, 'profile'):
                                profile = Profile.objects.create(user=cus_user)
                                profile.finished_signup = False
                                profile.save()
                                security_profile = SecurityProfile.objects.create(user=cus_user)
                                security_profile.save()
                            messages.success(request, 'You are now subscribed, check your email for a confirmation. When you get the chance, fill out the form below to make an account.')
                            send_verification_email(cus_user)
                            send_registration_push(cus_user)
                            sendwelcomeemail(cus_user)
                    except: pass
            from femmebabe.celery import validate_bitcoin_payment
            validate_bitcoin_payment.apply_async(timeout=60*5, args=(cus_user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), usd_fee,),)
            validate_bitcoin_payment.apply_async(timeout=60*10, args=(cus_user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), usd_fee,),)
            return redirect(reverse('payments:subscribe-bitcoin-thankyou', kwargs={'username': user.profile.name}))
    from payments.apis import get_crypto_price
    fee = str(int(user.vendor_profile.subscription_fee) / get_crypto_price(crypto))
    fee_reduced = fee.split('.')[0] + '.' + fee.split('.')[1][:settings.BITCOIN_DECIMALS]
    from payments.crypto import get_payment_address
    address, transaction_id = get_payment_address(user, crypto, float(fee_reduced))
    from femmebabe.celery import validate_bitcoin_payment
    validate_bitcoin_payment.apply_async(timeout=60*10, args=(request.user.id, user.id, float(fee_reduced) * settings.MIN_BITCOIN_PERCENTAGE, transaction_id, usd_fee,),)
    from feed.models import Post
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    from django.shortcuts import render
    return render(request, 'payments/subscribe_crypto.html', {'title': 'Subscribe with Crypto', 'model': user.profile, 'username': username, 'vendor_profile': profile, 'profile': profile, 'form': BitcoinPaymentForm(initial={'amount': str(fee_reduced), 'transaction_id': transaction_id}) if not request.user.is_authenticated else BitcoinPaymentFormUser(initial={'amount': str(fee_reduced), 'transaction_id': transaction_id}), 'crypto_address': address, 'crypto_fee': fee_reduced, 'usd_fee': usd_fee, 'currencies': settings.CRYPTO_CURRENCIES, 'post': post, 'model': user.profile})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip_bitcoin_thankyou(request, username):
    from django.contrib.auth.models import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    from django.shortcuts import render
    return render(request, 'payments/tip_bitcoin_thankyou.html', {'title': 'Thanks - {}', 'profile': user.profile})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip_bitcoin(request, username, tip):
    from django.conf import settings
    from django.shortcuts import redirect
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto')
    from django.contrib.auth.modles import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    from .models import VendorPaymentsProfile
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    from .forms import BitcoinPaymentFOrm
    if request.method == 'POST':
        form = BitcoinPaymentForm(request.POST)
        if form.is_valid():
            return redirect(reverse('payments:tip-bitcoin-thankyou', kwargs={'username': user.profile.name}))
    from .apis import get_crypto_price
    fee = str(int(tip) / get_crypto_price(crypto))
    fee_reduced = fee.split('.')[0] + '.' + fee.split('.')[1][:settings.BITCOIN_DECIMALS]
    usd_fee = tip
    from .crypto import get_payment_address
    address, transaction_id = get_payment_address(user, crypto, float(fee_reduced))
    from feed.models import Post
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    from django.shortcuts import render
    return render(request, 'payments/tip_crypto.html', {'title': 'Tip with Crypto', 'username': username, 'crypto_address': address, 'profile': profile, 'form': BitcoinPaymentForm(initial={'amount': str(fee_reduced)}), 'crypto_fee': fee_reduced, 'usd_fee': usd_fee, 'currencies': settings.CRYPTO_CURRENCIES, 'post': post})

def buy_photo_crypto(request, username):
    from security.middleware import get_qs
    from django.conf import settings
    from django.shortcuts import redirect
    from security.middleware import get_qs
    if not request.GET.get('crypto'): return redirect(request.path + get_qs(request.GET) + '&crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto')
    from django.contrib.auth.models import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    from payments.models import VendorPaymentsProfile
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    from feed.models import Post
    if not request.GET.get('id'): return redirect(request.path + '?crypto={}&id={}'.format(crypto, Post.objects.filter(author=user, private=False, public=False, published=True, recipient=None).exclude(image=None).order_by('?').first().uuid))
    id = request.GET.get('id', None)
    post = Post.objects.get(uuid=id)
    tip = int(post.price)
    from payments.forms import BitcoinPaymentForm, BitcoinPaymentFormUser
    if request.method == 'POST':
        form = BitcoinPaymentForm(request.POST) if not request.user.is_authenticated else BitcoinPaymentFormUser(request.POST)
        if form.is_valid():
            cus_user = User.objects.filter(profile__email=form.cleaned_data.get('email', None)).order_by('-last_seen')[0] if not request.user.is_authenticated else request.user
            if not (cus_user and cus_user.email != '' and cus_user.email != None):
                cus_user = None
                from email_validator import validate_email
                e = form.cleaned_data.get('email', None)
                if e:
                    try:
                        from security.apis import check_raw_ip_risk
                        from security.models import SecurityProfile
                        from users.models import Profile
                        from users.email import send_verification_email, sendwelcomeemail
                        from users.views import send_registration_push
                        valid = validate_email(e, check_deliverability=True)
                        us = User.objects.filter(email=e).last()
                        safe = not check_raw_ip_risk(ip, soft=True, dummy=False, guard=True)
                        if valid and not us and safe:
                            cus_user = User.objects.create(email=e, username=get_random_username(), password=get_random_string(length=8))
                            if not hasattr(cus_user, 'profile'):
                                profile = Profile.objects.create(user=cus_user)
                                profile.finished_signup = False
                                profile.save()
                                security_profile = SecurityProfile.objects.create(user=cus_user)
                                security_profile.save()
                            messages.success(request, 'You are now subscribed, check your email for a confirmation. When you get the chance, fill out the form below to make an account.')
                            send_verification_email(cus_user)
                            send_registration_push(cus_user)
                            sendwelcomeemail(cus_user)
                    except: pass
            from django.contrib import messages
            messages.success(request, 'We are validating your crypto payment. Please allow up to 15 minutes for this process to take place.')
            from femmebabe.celery import validate_photo_payment
            validate_photo_payment.apply_async(timeout=60*5, args=(cus_user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), id,),)
            validate_photo_payment.apply_async(timeout=60*10, args=(cus_user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), id,),)
            return redirect(reverse('feed:post-detail', kwargs={'id': id}))
    from .apis import get_crypto_price
    fee = str(int(tip) / get_crypto_price(crypto))
    fee_reduced = fee.split('.')[0] + '.' + fee.split('.')[1][:settings.BITCOIN_DECIMALS]
    usd_fee = tip
    from .crypto import get_payment_address
    address, transaction_id = get_payment_address(user, crypto, float(fee_reduced))
    from django.shortcuts import render
    if request.user.is_authenticated:
        from femmebabe.celery import validate_photo_payment
        validate_photo_payment.apply_async(timeout=60*5, args=(request.user.id, user.id, float(fee_reduced) * settings.MIN_BITCOIN_PERCENTAGE, transaction_id, id,),)
    return render(request, 'payments/buy_photo_crypto.html', {'title': 'Buy photo with Crypto', 'username': username, 'crypto_address': address, 'profile': profile, 'form': BitcoinPaymentForm(initial={'amount': str(fee_reduced), 'transaction_id': transaction_id}) if not request.user.is_authenticated else BitcoinPaymentFormUser(initial={'amount': str(fee_reduced), 'transaction_id': transaction_id}), 'crypto_fee': fee_reduced, 'usd_fee': usd_fee, 'currencies': settings.CRYPTO_CURRENCIES, 'post': post})

@cache_page(60*60*24*7)
def buy_photo_card(request, username):
    from security.middleware import get_qs
    from django.contrib.auth.models import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    from payments.models import VendorPaymentsProfile
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    fee = user.vendor_profile.photo_tip
    from django.shortcuts import redirect
    from feed.models import Post
    if not request.GET.get('id'): return redirect(request.path + (get_qs(request.GET) if len(request.GET) > 0 else '?') + '&id={}'.format(Post.objects.filter(author=user, private=False, public=False, published=True, recipient=None).exclude(image=None).order_by('?').first().uuid))
    id = request.GET.get('id', None)
    post = Post.objects.get(uuid=id)
    from django.shortcuts import render
    from django.conf import settings
    r = render(request, 'payments/buy_photo_card.html', {'title': 'Buy this photo with Credit or Debit Card', 'username': username, 'profile': profile, 'fee': post.price, 'post': post, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def charge_card(request):
    user = request.user
    from .forms import CardNumberForm, PaymentForm
    from .models import VendorPaymentsProfile, PaymentCard, CardPayment
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    if request.method == 'POST':
        from django.contrib import messages
        num_form = CardNumberForm(request.user,request.POST)
        card = None
        if num_form.is_valid():
            if PaymentCard.objects.filter(user=request.user, number=num_form.cleaned_data.get('number')).count() > 0: card = PaymentCard.objects.filter(user=request.user, number=num_form.cleaned_data.get('number')).last()
            else: card = num_form.save()
        else:
            messages.warning(request, num_form.errors)
        info_form = CardInfoForm(request.user, request.POST, instance=card)
        if info_form.is_valid():
            if form.cleaned_data.get('expiry_month') != 'MM' and form.cleaned_data.get('expiry_year') != 'YY':
                card = info_form.save()
            else:
                messages.warning(request, 'Please choose an expiration date in the form.')
                card.delete()
                card = None
        else:
            messages.warning(request, info_form.errors)
            card.delete()
        if card:
            payment_form = PaymentForm(request.POST)
#            from payments.authorizenet import pay_fee
            if not payment_form.is_valid(): messages.warning(request, 'The form could not be validated.')
#            elif pay_fee(user, payment_form.cleaned_data.get('total'), card, customer_type=payment_form.cleaned_data.get('customer_type'), full_name=payment_form.cleaned_data.get('full_name'), name=payment_form.cleaned_data.get('item_name'), description=payment_form.cleaned_data.get('description')):
            if False:
                messages.success(request, 'The payment was processed.')
                from django.shortcuts import redirect
                from django.urls import reverse
                return redirect(reverse('go:go'))
            else:
                messages.warning(request, 'Your payment wasn\'t processed successfully. Please try a new form of payment.')
    from django.shortcuts import render
    return render(request, 'payments/charge_card.html', {'title': 'Charge a Credit or Debit Card', 'card_info_form': CardInfoForm(request.user), 'card_number_form': CardNumberForm(request.user), 'payment_form': PaymentForm(), 'username': profile.vendor.profile.name})

@cache_page(60*60*3)
def tip_crypto_simple(request, username):
    from django.shortcuts import redirect
    from django.conf import settings
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto')
    from django.contrib.auth.models import User
    user = User.objects.get(profile__name=username, profile__vendor=True)
    from payments.models import VendorPaymentsProfile
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    from payments.crypto import get_payment_address
    address, transaction_id = get_payment_address(user, crypto, float(1000))
    from feed.models import Post
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    from django.shortcuts import render
    r = render(request, 'payments/tip_crypto_simple.html', {'title': 'Send a Tip in Crypto', 'address': address, 'currencies': settings.CRYPTO_CURRENCIES, 'username': user.profile.name, 'post': post})
    if request.user.is_authenticated: patch_cache_control(r, private=True)
    else: patch_cache_control(r, public=True)
    return r
