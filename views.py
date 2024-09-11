from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from vendors.tests import is_vendor
from feed.tests import identity_verified, identity_really_verified
from django.contrib.sessions.models import Session
from security.views import all_unexpired_sessions_for_user
from django.contrib.auth.models import User
from django.contrib import messages
from .models import CustomerPaymentsProfile, VendorPaymentsProfile, CardPayment
from .forms import BitcoinPaymentForm, PaymentForm
from .apis import get_crypto_price
from lotteh.celery import validate_bitcoin_payment
from django.conf import settings
from .forms import CardNumberForm, CardInfoForm
from .authorizenet import pay_fee
from .crypto import get_payment_address
from django.http import HttpResponse, JsonResponse
from feed.models import Post
from .models import PaymentCard, PurchasedProduct
from django.views.decorators.csrf import csrf_exempt
from users.tfa import send_user_text
import random
from django.utils.crypto import get_random_string
from users.email import send_verification_email
from users.username_generator import generate_username
from users.password_reset import send_password_reset_email
from feed.templatetags.nts import nts
from contact.forms import ContactForm

def render_agreement(name, parent, mother):
    from django.template.loader import render_to_string
    return render_to_string('payments/surrogacy.txt', {
        'the_clinic_name': settings.FERTILITY_CLINIC,
        'the_site_name': settings.SITE_NAME,
        'mother_name': name,
        'mother_address': mother.vendor_profile.address,
        'mother_insurance': mother.vendor_profile.insurance_provider,
        'the_state_name': 'Washington',
        'parent_name': parent,
        'surrogacy_fee': nts(settings.SURROGACY_FEE),
        'the_date': timezone.now().strftime('%B %d, %Y'),
    })

def cancel(request):
    return render(request, 'payments/cancel_payment.html', {'title':'We\'re sad to see you go'})

def success(request):
    return render(request, 'payments/success.html', {'title': 'Thank you for your payment'})

def webdev(request):
    from payments.stripe import WEBDEV_DESCRIPTIONS
    prices = ['100', '200', '500', '1000', '2000', '5000']
    price_dev = []
    for x in range(0, len(prices)):
        price_dev = price_dev + [{'price': prices[x], 'description': WEBDEV_DESCRIPTIONS[x]}]
    return render(request, 'payments/webdev.html', {'title': 'Web Development Pricing', 'plans': price_dev, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'email_query_delay': 30, 'contact_form': ContactForm()})

def idscan(request):
    price_scans = ['5','10', '20', '50', '100', '200', '500', '1000', '2000', '5000']
    return render(request, 'payments/idscan.html', {'title': 'ID Scanner Pricing', 'plans': price_scans, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'email_query_delay': 30, 'free_trial': settings.IDSCAN_TRIAL_DAYS})

def surrogacy(request, username):
    vendor = User.objects.get(profile__name=username, profile__vendor=True)
    agreement = render_agreement(vendor.profile.name if not vendor.verifications.last() else vendor.verifications.last().full_name, request.user.verifications.last().full_name if request.user.is_authenticated and request.user.verifications.last() else '', vendor)
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    return render(request, 'payments/surrogacy.html', {'title': 'Surrogacy Plans', 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'post': post, 'vendor': vendor, 'agreement': agreement, 'surrogacy_fee': settings.SURROGACY_FEE,})

def surrogacy_info(request, username):
    vendor = User.objects.get(profile__name=username, profile__vendor=True)
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    return render(request, 'payments/surrogacy_info.html', {'title': 'Surrogacy Plan Information', 'post': post, 'vendor': vendor, 'surrogacy_fee': settings.SURROGACY_FEE, 'contact_form': ContactForm()})


@login_required
@user_passes_test(identity_really_verified, login_url='/verify/', redirect_field_name='next')
def connect_account(request):
    from .stripe import create_connected_account
    return redirect(create_connected_account(request.user.id))

@login_required
def model_subscription_cancel(request, username):
    import stripe
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
    from payments.stripe import PRICE_IDS
    from payments.stripe import PROFILE_MEMBERSHIP_PRICE_IDS
    from payments.stripe import PHOTO_PRICE_IDS
    from payments.stripe import WEBDEV_PRICE_IDS
    from payments.stripe import WEBDEV_MONTHLY_PRICE_IDS
    from payments.stripe import WEBDEV_DESCRIPTIONS
    price_scans = ['5','10', '20', '50', '100', '200', '500', '1000', '2000', '5000']
    price_dev = ['100', '200', '500', '1000', '2000', '5000']
    try:
        event = stripe.Event.construct_from(
            json.loads(payload), settings.STRIPE_API_KEY
        )
    except ValueError as e:
        return HttpResponse(status=400)
    if event.type == 'checkout.session.completed' or event.type == 'charge.created':
        session = event.data['object']
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get("subscription")
        stripe_price_id = session.get("price")
        account = session.get("account")
        metadata = session.get("metadata")
        email = session.get("receipt_email")
        user = None
        if User.objects.filter(email=email).count() < 1:
            user = User.objects.create(email=email, username=generate_username(), password=get_random_string(8))
            client_reference_id = user.id
            user.profile.stripe_customer_id = stripe_customer_id
            if stripe_price_id in WEBDEV_MONTHLY_PRICE_IDS:
                user.profile.stripe_subscription_service_id = stripe_subscription_id
            else:
                user.profile.stripe_subscription_id = stripe_subscription_id
            user.profile.save()
            send_verification_email(user)
            send_password_reset_email(user)
        else:
            user = User.objects.get(id = client_reference_id)
            user.profile.stripe_customer_id = stripe_customer_id,
            if stripe_price_id in WEBDEV_MONTHLY_PRICE_IDS:
                user.profile.stripe_subscription_service_id = stripe_subscription_id
            else:
                user.profile.stripe_subscription_id = stripe_subscription_id
            user.profile.save()
        try:
            plan = PRICE_IDS.index(stripe_price_id)
            user.profile.idscan_plan = int(price_scans[plan]) * 2
            user.profile.idscan_active = True
            user.profile.idscan_used = 0
            user.profile.save()
            user.save()
            send_user_text(User.objects.get(id=settings.MY_ID), '@{} has purchased an ID scanner subscription product for ${}'.format(user.username, price_scans[plan]))
        except:
            try:
                product = WEBDEV_PRICE_IDS.index(stripe_price_id)
                product_desc = WEBDEV_DESCRIPTIONS[product]
                PurchasedProduct.objects.create(user=user, description=product_desc, price=int(price_dev[product]), paid=True)
                send_user_text(User.objects.get(id=settings.MY_ID), '@{} has purchased a web dev product for ${} - "{}"'.format(user.username, price_dev[product], product_desc))
            except:
                try:
                    product = PROFILE_MEMBERSHIP_PRICE_IDS.index(stripe_price_id)
                    if account:
                        vendor = User.objects.get(profile__stripe_id=account)
                        user.profile.subscriptions.add(vendor)
                        user.profile.save()
                        if not Subscription.objects.filter(model=vendor, user=user, active=True).last(): Subscription.objects.create(model=vendor, user=user, active=True, strip_subscription_id=stripe_subscription_id)
                except:
                    try:
                        product = PHOTO_PRICE_IDS.index(stripe_price_id)
                        vendor = User.objects.get(profile__stripe_id=account)
                        post = Post.objects.get(author=vendor, uuid=metadata[0])
                        post.recipient = user
                        post.save()
                    except:
                        from .stripe import SURROGACY_PRICE_ID
                        if SURROGACY_PRICE_ID == stripe_price_id:
                            send_user_text(User.objects.get(id=settings.MY_ID), '{} (@{}) has purchased a surrogacy plan with you. Please update them with details.'.format(user.verifications.last().full_name, user.username))
                        else:
                            try:
                                product = WEBDEV_MONTHLY_PRICE_IDS.index(stripe_price_id)
                                if product != None:
                                    user.profile.webdev_plan = int(price_dev[product])
                                    user.profile.webdev_active = True
                                    user.profile.save()
                                    PurchasedProduct.objects.create(user=user, description=product_desc, price=int(price_dev[product]), paid=True, monthly=True)
                                    send_user_text(User.objects.get(id=settings.MY_ID), '@{} has purchased a web dev product for ${} - "{}"'.format(user.username, price_dev[product], product_desc))
                            except: pass
    elif event.type == 'charge.failed' or event.type == 'charge.refunded':
        session = event.data['object']
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get("subscription")
        try:
            plan = PRICE_IDS.index(stripe_price_id)
            user = User.objects.get(profile__stripe_customer_id=stripe_customer_id)
            user.profile.idscan_active = False
            user.profile.save()
            user.save()
        except:
            product = PROFILE_MEMBERSHIP_PRICE_IDS.index(stripe_price_id)
            if product != None and account:
                vendor = User.objects.get(profile__stripe_id=account)
                user.profile.subscriptions.remove(vendor)
                user.profile.save()
    else:
        print('Unhandled event type {}'.format(event.type))
    return HttpResponse(status=200)

@csrf_exempt
def monthly_checkout_profile(request):
    import stripe
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
    photo = request.GET.get('photo')
    vendor = Post.objects.filter(id=str(photo)).first().author
    prices = [5, 10, 20, 25, 50, 100]
    id = prices.index(int(Post.objects.filter(id=str(photo)).first().price))
    from payments.stripe import PHOTO_PRICE_IDS
    price = PHOTO_PRICE_IDS[id]
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
    from payments.stripe import SURROGACY_PRICE_ID
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
    cards = PaymentCard.objects.filter(user=request.user).order_by('-primary')
    return render(request, 'payments/payment_cards.html', {'title': 'Payment Cards', 'cards': cards})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def card_primary(request, id):
    if request.method == 'POST':
        card = PaymentCard.objects.filter(id=int(id)).first()
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
    if request.method == 'POST':
        card = PaymentCard.objects.filter(id=int(id)).first()
        messages.success(request, 'The card ending in *{} was deleted.'.format(str(card.number if card and card.number else '****************')[12:]))
        if card: card.delete()
    return HttpResponse('Deleted')


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def cancel_subscription(request, username):
    model = User.objects.get(profile__name=username, profile__vendor=True)
    if not model in request.user.profile.subscriptions.all():
        return redirect(reverse('feed:profile', kwargs={'username': model.profile.name}))
    fee = model.vendor_profile.subscription_fee
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_API_KEY
        stripe.Subscription.delete(sub.stripe_subscription_id)
        sub = Subscription.objects.filter(active=True, model=model, user=request.user).last()
        sub.active = False
        sub.save()
        request.user.profile.subscriptions.delete(remove)
        request.user.profile.save()
        messages.success(request, 'You have cancelled your subscription.')
        return redirect(reverse('feed:home'))
    return render(request, 'payments/cancel.html', {
        'title': 'Cancel Subscription',
        'model': model
    })

def subscribe_card(request, username):
    user = User.objects.get(profile__name=username, profile__vendor=True)
    if hasattr(request, 'user') and request.user.is_authenticated and user in request.user.profile.subscriptions.all():
        return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
    profile = user.profile
    fee = user.vendor_profile.subscription_fee
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    return render(request, 'payments/subscribe_card.html', {'title': 'Subscribe', 'username': username, 'profile': profile, 'fee': fee, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY, 'model': user.profile, 'post': post})


@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip_card(request, username, tip):
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
            if pay_fee(user, fee, card, name='Tip to {}\'s profile'.format(user.profile.name), description='One time tip for adult webcam modeling content.'):
                CardPayment.objects.create(user=request.user, amount=fee)
                send_user_text(user, '{} has tipped you ${}, {}.'.format(request.user.profile.name, fee, user.profile.preferred_name))
                messages.success(request, 'Your payment was processed. Thank you for the tip!')
                return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
            else:
                messages.warning(request, 'Your payment wasn\'t processed successfully. Please try a new form of payment.')
    return render(request, 'payments/tip_card.html', {'title': 'Tip With Credit or Debit Card', 'username': username, 'profile': profile, 'card_info_form': CardInfoForm(request.user), 'card_number_form': CardNumberForm(request.user, initial={'address': request.user.verifications.last().address if request.user.verifications.last() else ''}), 'fee': fee, 'username': username, 'profile': profile, 'usd_fee': fee})



@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def subscribe_bitcoin_thankyou(request, username):
    user = User.objects.get(profile__name=username, profile__vendor=True)
    if user in request.user.profile.subscriptions.all():
        messages.success(request, 'Your payment has been verified. Thank you for subscribing! - {}'.format(user.profile.name))
        return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
    return render(request, 'payments/subscribe_bitcoin_thankyou.html', {'title': 'Thanks - {}', 'profile': user.profile})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def subscribe_bitcoin(request, username):
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto') if request.GET.get('crypto') else 'BTC'
    user = User.objects.get(profile__name=username, profile__vendor=True)
    if user in request.user.profile.subscriptions.all():
        return redirect(reverse('feed:profile', kwargs={'username': user.profile.name}))
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    usd_fee = user.vendor_profile.subscription_fee
    if request.method == 'POST':
        form = BitcoinPaymentForm(request.POST)
        if form.is_valid():
            messages.success(request, 'We are validating your crypto payment. Please allow up to 15 minutes for this process to take place.')
            validate_bitcoin_payment.apply_async(timeout=60*5, args=(request.user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), usd_fee,),)
            validate_bitcoin_payment.apply_async(timeout=60*10, args=(request.user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), usd_fee,),)
            return redirect(reverse('payments:subscribe-bitcoin-thankyou', kwargs={'username': user.profile.name}))
    fee = str(int(user.vendor_profile.subscription_fee) / get_crypto_price(crypto))
    fee_reduced = fee.split('.')[0] + '.' + fee.split('.')[1][:settings.BITCOIN_DECIMALS]
    address, transaction_id = get_payment_address(user, crypto, float(fee_reduced))
    validate_bitcoin_payment.apply_async(timeout=60*10, args=(request.user.id, user.id, float(fee_reduced) * settings.MIN_BITCOIN_PERCENTAGE, transaction_id, usd_fee,),)
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    return render(request, 'payments/subscribe_crypto.html', {'title': 'Subscribe with Crypto', 'model': user.profile, 'username': username, 'vendor_profile': profile, 'profile': profile, 'form': BitcoinPaymentForm(initial={'amount': str(fee_reduced), 'transaction_id': transaction_id}), 'crypto_address': address, 'crypto_fee': fee_reduced, 'usd_fee': usd_fee, 'currencies': settings.CRYPTO_CURRENCIES, 'post': post, 'model': user.profile})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip_bitcoin_thankyou(request, username):
    user = User.objects.get(profile__name=username, profile__vendor=True)
    return render(request, 'payments/tip_bitcoin_thankyou.html', {'title': 'Thanks - {}', 'profile': user.profile})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def tip_bitcoin(request, username, tip):
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto')
    user = User.objects.get(profile__name=username, profile__vendor=True)
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    if request.method == 'POST':
        form = BitcoinPaymentForm(request.POST)
        if form.is_valid():
            return redirect(reverse('payments:tip-bitcoin-thankyou', kwargs={'username': user.profile.name}))
    fee = str(int(tip) / get_crypto_price(crypto))
    fee_reduced = fee.split('.')[0] + '.' + fee.split('.')[1][:settings.BITCOIN_DECIMALS]
    usd_fee = tip
    address, transaction_id = get_payment_address(user, crypto, float(fee_reduced))
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    return render(request, 'payments/tip_crypto.html', {'title': 'Tip with Crypto', 'username': username, 'crypto_address': address, 'profile': profile, 'form': BitcoinPaymentForm(initial={'amount': str(fee_reduced)}), 'crypto_fee': fee_reduced, 'usd_fee': usd_fee, 'currencies': settings.CRYPTO_CURRENCIES, 'post': post})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
def buy_photo_crypto(request, username):
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto')
    user = User.objects.get(profile__name=username, profile__vendor=True)
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    tip = user.vendor_profile.photo_tip
    if not request.GET.get('id'): return redirect(request.path + '?crypto={}&id={}'.format(crypto, Post.objects.filter(author=user, private=False, public=False, published=True, recipient=None).exclude(image=None).order_by('?').first().uuid))
    id = request.GET.get('id', None)
    post = Post.objects.get(uuid=id)
    if request.method == 'POST':
        form = BitcoinPaymentForm(request.POST)
        if form.is_valid():
            messages.success(request, 'We are validating your crypto payment. Please allow up to 15 minutes for this process to take place.')
            validate_photo_payment.apply_async(timeout=60*5, args=(request.user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), id,),)
            validate_photo_payment.apply_async(timeout=60*10, args=(request.user.id, user.id, float(form.data['amount']) * settings.MIN_BITCOIN_PERCENTAGE, form.cleaned_data.get('transaction_id'), id,),)
            return redirect(reverse('feed:post-detail', kwargs={'id': id}))
#            return redirect(reverse('payments:tip-bitcoin-thankyou', kwargs={'username': user.profile.name}))
    fee = str(int(tip) / get_crypto_price(crypto))
    fee_reduced = fee.split('.')[0] + '.' + fee.split('.')[1][:settings.BITCOIN_DECIMALS]
    usd_fee = tip
    address, transaction_id = get_payment_address(user, crypto, float(fee_reduced))
    return render(request, 'payments/buy_photo_crypto.html', {'title': 'Buy photo with Crypto', 'username': username, 'crypto_address': address, 'profile': profile, 'form': BitcoinPaymentForm(initial={'amount': str(fee_reduced)}), 'crypto_fee': fee_reduced, 'usd_fee': usd_fee, 'currencies': settings.CRYPTO_CURRENCIES, 'post': post})

def buy_photo_card(request, username):
    user = User.objects.get(profile__name=username, profile__vendor=True)
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    fee = user.vendor_profile.photo_tip
    if not request.GET.get('id'): return redirect(request.path + '?id={}'.format(Post.objects.filter(author=user, private=False, public=False, published=True, recipient=None).exclude(image=None).order_by('?').first().uuid))
    id = request.GET.get('id', None)
    post = Post.objects.get(uuid=id)
    return render(request, 'payments/buy_photo_card.html', {'title': 'Buy this photo with Credit or Debit Card', 'username': username, 'profile': profile, 'fee': fee, 'post': post, 'stripe_pubkey': settings.STRIPE_PUBLIC_KEY})

@login_required
@user_passes_test(identity_verified, login_url='/verify/', redirect_field_name='next')
@user_passes_test(is_vendor)
def charge_card(request):
    user = request.user
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
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
            if not payment_form.is_valid(): messages.warning(request, 'The form could not be validated.')
            elif pay_fee(user, payment_form.cleaned_data.get('total'), card, customer_type=payment_form.cleaned_data.get('customer_type'), full_name=payment_form.cleaned_data.get('full_name'), name=payment_form.cleaned_data.get('item_name'), description=payment_form.cleaned_data.get('description')):
                messages.success(request, 'The payment was processed.')
                return redirect(reverse('go:go'))
            else:
                messages.warning(request, 'Your payment wasn\'t processed successfully. Please try a new form of payment.')
    return render(request, 'payments/charge_card.html', {'title': 'Charge a Credit or Debit Card', 'card_info_form': CardInfoForm(request.user), 'card_number_form': CardNumberForm(request.user), 'payment_form': PaymentForm(), 'username': profile.vendor.profile.name})


def tip_crypto_simple(request, username):
    if not request.GET.get('crypto'): return redirect(request.path + '?crypto={}'.format(settings.DEFAULT_CRYPTO))
    crypto = request.GET.get('crypto')
    user = User.objects.get(profile__name=username, profile__vendor=True)
    profile, created = VendorPaymentsProfile.objects.get_or_create(vendor=user)
    address, transaction_id = get_payment_address(user, crypto, float(1000))
    post_ids = Post.objects.filter(public=True, private=False, published=True).exclude(image=None).order_by('-date_posted').values_list('id', flat=True)[:settings.FREE_POSTS]
    post = Post.objects.filter(id__in=post_ids).order_by('?').first()
    return render(request, 'payments/tip_crypto_simple.html', {'title': 'Send a Tip in Crypto', 'address': address, 'currencies': settings.CRYPTO_CURRENCIES, 'username': user.profile.name, 'post': post})
