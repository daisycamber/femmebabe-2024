# Generated by Django 4.2.5 on 2023-10-04 16:02

import address.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorPaymentsProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sub_partner_id', models.TextField(blank=True, default=None, null=True)),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_payments_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('expire_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('fee', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('stripe_subscription_id', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_subscribers', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_subscriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PurchasedProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('price', models.IntegerField(default=0)),
                ('paid', models.BooleanField(default=False)),
                ('pay_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchased_products', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentLink',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('stripe_id', models.CharField(blank=True, max_length=100, null=True)),
                ('url', models.CharField(blank=True, max_length=300, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('pay_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_links', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentCard',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('number', models.IntegerField(null=True)),
                ('expiry_month', models.CharField(max_length=2, null=True)),
                ('expiry_year', models.CharField(max_length=4, null=True)),
                ('cvv_code', models.IntegerField(null=True)),
                ('zip_code', models.IntegerField(null=True)),
                ('primary', models.BooleanField(default=True)),
                ('address', address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='address.address')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_cards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='IDScanSubscription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('active', models.BooleanField(default=False)),
                ('subscribe_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idware_privledge', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerPaymentsProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bitcoin_address', models.CharField(blank=True, default='', max_length=34, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customer_payments_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CardPayment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.FloatField()),
                ('index', models.IntegerField(default=0)),
                ('transaction_id', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='card_payments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BitcoinPayment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.FloatField()),
                ('index', models.IntegerField(default=0)),
                ('transaction_id', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bitcoin_payments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
