PRICE_IDS = ["price_1NqSBIDNUMHo0j8JyMJoFcJl", "price_1NqSBIDNUMHo0j8JbtvVS5pT", "price_1NqSBIDNUMHo0j8JPR4iYPmY", "price_1NqSBIDNUMHo0j8JgOigQC2I", "price_1NqSBIDNUMHo0j8JrlwK12jz", "price_1NqSBIDNUMHo0j8JZWSZpU3A", "price_1NqSBIDNUMHo0j8JJNChQvJM", "price_1NqSBIDNUMHo0j8Joimlo0kE", "price_1NqSBIDNUMHo0j8JvYF7XvRG", "price_1NqSBIDNUMHo0j8J5WV0aUX3"]
WEBDEV_PRICE_IDS = ["price_1NqS9SDNUMHo0j8JM4dCImE0", "price_1NqS9SDNUMHo0j8JW1Muzlf4", "price_1NqS9SDNUMHo0j8J2gHVo7yd", "price_1NqS9SDNUMHo0j8JJwHNpStV", "price_1NqS9TDNUMHo0j8JKMzqGIBv", "price_1NqS9TDNUMHo0j8Jy3RA8fw5"]
WEBDEV_MONTHLY_PRICE_IDS = ["price_1ObFDTDNUMHo0j8JKmX3FKsW", "price_1ObFDcDNUMHo0j8J1ft3uhf8", "price_1ObFDlDNUMHo0j8JAK5B0GgL", "price_1ObFDsDNUMHo0j8JqS5IeNxK", "price_1ObFDzDNUMHo0j8JqHKhtuNM", "price_1ObFEBDNUMHo0j8JZbhoKEst"]
#"price_1Koi4MDNUMHo0j8JUjVdK5ZA", "price_1KoVXmDNUMHo0j8JMyudvUja", "price_1Nqp3VDNUMHo0j8JY6soNnfk", "price_1Koi4VDNUMHo0j8JsLO8HabI", "price_1NqgdRDNUMHo0j8JAmUB03Kv", "price_1Koi4MDNUMHo0j8JUjVdK5ZA", "price_1KoVXmDNUMHo0j8JMyudvUja",
PROFILE_MEMBERSHIP_PRICE_IDS = ["price_1Koi4MDNUMHo0j8JUjVdK5ZA", "price_1KoVXmDNUMHo0j8JMyudvUja", "price_1Nqp3VDNUMHo0j8JY6soNnfk", "price_1Koi4VDNUMHo0j8JsLO8HabI", "price_1NqgdRDNUMHo0j8JAmUB03Kv", "price_1Koi4bDNUMHo0j8JauWHhYQA", "price_1NqgdgDNUMHo0j8JdknpoCgx", "price_1Koi4iDNUMHo0j8Js6rMAm3K", "price_1NqgfHDNUMHo0j8JyRky2t3w", "price_1NqgfMDNUMHo0j8JpWmXfSOh", "price_1NqgfTDNUMHo0j8Jc1UsGaHo", "price_1NqgfaDNUMHo0j8JMllYt5sL"]
PROFILE_MEMBERSHIP = "prod_LVWaXfmwmUQUg6"
PHOTO_PRICE = "prod_OdjZX8kiImqMHs"
PHOTO_PRICE_IDS = ["price_1NqS6fDNUMHo0j8JSsibkHw7", "price_1NqS6fDNUMHo0j8JRl4UFBZv", "price_1NqS6fDNUMHo0j8JC15M3yPW", "price_1NqS6fDNUMHo0j8JJdkeCaUB", "price_1NqS6fDNUMHo0j8Jm9ocRrHv", "price_1NqS6fDNUMHo0j8Jocts6Mkh"]
WEBDEV_DESCRIPTIONS = ["Simple, static website. Ideal for businesses that don't need interactivity, just a business page with contacts, information, and photos.",
    "Basic website with simple interactivity, modals, and user logins. Ideal for small businesses that don't need complex interactivity or marketing.",
    "Complex website with email marketing. Ideal for small to mid sized businesses, campaigns, and websites that need basic marketing features and many pages.",
    "Complex website with email, SMS, webpush, Google News, and social marketing features. Good for mid-size businesses with marketing needs.",
    "Advanced website with security options, scalable design, image and video uploads, comprehensive compliance features, bluetooth capability, 3D rendering, negotiable options. Ideal for scientific and industrial needs in large scale businesses.",
    "Advanced website with facial recognition, biometric security, advanced login, custom authentication, barcode scanning, machine learning and more. Preceding features included. Ideal for large projects and governments. Multiple options available.",
]
SURROGACY_PRICE_ID = "price_1OBuzfDNUMHo0j8JEKdChyTl"
CART_ID = ""

import stripe
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User

def create_connected_account(user_id):
    stripe.api_key = settings.STRIPE_API_KEY
    user = User.objects.get(id=user_id)
    if not user.profile.stripe_id:
        account = stripe.Account.create(
            type='custom',
            country='US',
            email=user.email,
            capabilities={
                "transfers": {"requested": True},
            },
        )
        user.profile.stripe_id = account.id
        user.profile.save()
    return stripe.AccountLink.create(
        account=user.profile.stripe_id,
        refresh_url=settings.BASE_URL + reverse('payments:create-link'),
        return_url=settings.BASE_URL + reverse('users:profile'),
        type="account_onboarding",
    )['url']
