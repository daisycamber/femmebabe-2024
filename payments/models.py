from simple_history.models import HistoricalRecords
from django.db import models
from django.contrib.auth.models import User
from subprocess import check_output
import subprocess
import re
from django.utils import timezone
from shell.execute import run_command
from payments.crypto import get_payment_status, get_sub_partner_balance, generate_sub_partner
from address.models import AddressField

class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoice', null=True)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_invoice', null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    price = models.IntegerField(default=0)
    pid = models.IntegerField(default=0)
    product = models.CharField(max_length=100, default='', null=True, blank=True)
    processor = models.CharField(max_length=100, default='', null=True, blank=True)
    number = models.CharField(max_length=100, default='', null=True, blank=True)
    token = models.CharField(max_length=100, default='', null=True, blank=True)
    cart = models.TextField(default='', null=True, blank=True)

class IDScanSubscription(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='idware_privledge')
    active = models.BooleanField(default=False)
    subscribe_date = models.DateTimeField(default=timezone.now)

class PaymentLink(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_links')
    stripe_id = models.CharField(max_length=100, null=True, blank=True)
    url = models.CharField(null=True, blank=True, max_length=300)
    paid = models.BooleanField(default=False)
    pay_date = models.DateTimeField(default=timezone.now)

class PurchasedProduct(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products')
    description = models.CharField(max_length=1000, null=True, blank=True)
    price = models.IntegerField(default=0)
    paid = models.BooleanField(default=False)
    pay_date = models.DateTimeField(default=timezone.now)

class PaymentCard(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_cards')
    number = models.IntegerField(null=True)
    expiry_month = models.CharField(null=True, max_length=2)
    expiry_year = models.CharField(null=True, max_length=4)
    cvv_code = models.IntegerField(null=True)
    address = AddressField(null=True, blank=True)
    zip_code = models.IntegerField(null=True)
    primary = models.BooleanField(default=True)

class Subscription(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_subscriptions')
    model = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_subscribers')
    expire_date = models.DateTimeField(default=timezone.now)
    fee = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=100,default='', null=True, blank=True)

class CardPayment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_payments')
    amount = models.FloatField()
    index = models.IntegerField(default=0)
    transaction_id = models.CharField(max_length=100, default='', null=True, blank=True)


class BitcoinPayment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bitcoin_payments')
    amount = models.FloatField()
    index = models.IntegerField(default=0)
    transaction_id = models.CharField(max_length=100, default='', null=True, blank=True)

class ValidatedTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=100, default='', null=True, blank=True)

# Create your models here.
class VendorPaymentsProfile(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_payments_profile')
    sub_partner_id = models.TextField(default=None, null=True, blank=True)

    def __str__(self):
        return 'user {} name "{}" {}'.format(self.vendor.profile.name, self.vendor.verifications.first().full_name, self.bitcoin_address.split(',')[0])

    def get_sub_partner_id(self):
        return None
        if self.sub_partner_id:
            return self.sub_partner_id
        else:
            try:
                self.sub_partner_id = generate_sub_partner(self.vendor.id)
            except Exception as e:
                print(e.stderr)
            self.save()
            return self.sub_partner_id

    def validate_crypto_transaction(self, user, min_balance, id):
        from django.conf import settings
        if get_payment_status(id) > float(min_balance) * (settings.MIN_CRYPTO_PERCENTAGE/100.0):
            if ValidatedTransaction.objects.filter(uid=id).count() > 0: return False
            ValidatedTransaction.objects.create(uid=id)
            return True
        return False

    def get_crypto_balances(self):
        if not self.sub_partner_id:
            self.sub_partner_id = generate_sub_partner(self.vendor.id)
            self.save()
        return get_sub_partner_balance(self.sub_partner_id)

    def save(self, *args, **kwargs):
        super(VendorPaymentsProfile, self).save(*args, **kwargs)

class CustomerPaymentsProfile(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_payments_profile')
    bitcoin_address = models.CharField(default='', null=True, blank=True, max_length=34)

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (str(uuid.uuid4()), ext)
    return os.path.join('surrogacy/', filename)

class SurrogacyPlan(models.Model):
    id = models.AutoField(primary_key=True)
    mother = models.ForeignKey(User, related_name='surrogacy_plans', null=True, blank=True, on_delete=models.DO_NOTHING)
    expected_parent = models.ForeignKey(User, related_name='parents_plans', null=True, blank=True, on_delete=models.DO_NOTHING)
    expected_parents_partner = models.ForeignKey(User, related_name='parents_partners_plans', null=True, blank=True, on_delete=models.DO_NOTHING)
    agreement = models.FileField(null=True, blank=True, upload_to=get_file_path, max_length=500)
    signed = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
