# Generated by Django 4.2.5 on 2023-10-13 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_profile_can_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='enable_facial_recognition',
            field=models.BooleanField(default=True),
        ),
    ]
