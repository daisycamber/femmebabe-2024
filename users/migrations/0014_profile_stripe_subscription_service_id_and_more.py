# Generated by Django 5.0.1 on 2024-01-22 04:42

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_mfatoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stripe_subscription_service_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='webdev_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='webdev_plan',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='profile',
            name='face_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='interactive',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='interactive_uuid',
            field=models.CharField(blank=True, default='', max_length=36, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='ip',
            field=models.CharField(blank=True, default='', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='stripe_customer_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='stripe_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='timezone',
            field=models.CharField(blank=True, default='', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='uuid',
            field=models.CharField(default=uuid.uuid4, max_length=36),
        ),
    ]
