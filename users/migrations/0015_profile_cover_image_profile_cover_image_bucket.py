# Generated by Django 5.0.1 on 2024-03-11 22:58

import feed.storage
import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_profile_stripe_subscription_service_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='cover_image',
            field=models.ImageField(default='default.png', upload_to=users.models.get_image_path),
        ),
        migrations.AddField(
            model_name='profile',
            name='cover_image_bucket',
            field=models.ImageField(blank=True, max_length=500, null=True, storage=feed.storage.MediaStorage(), upload_to=users.models.get_image_path),
        ),
    ]
