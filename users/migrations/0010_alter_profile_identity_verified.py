# Generated by Django 4.2.6 on 2023-11-05 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_profile_shop_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='identity_verified',
            field=models.BooleanField(default=False),
        ),
    ]
