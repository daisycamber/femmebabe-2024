# Generated by Django 5.0.6 on 2024-05-15 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_alter_profile_email_password_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='email_password',
            field=models.CharField(blank=True, default='Sj7YHcsO', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='idscan_api_key',
            field=models.CharField(blank=True, default='9a5a0ca7-5181-4db9-bc61-9e98c795a16f', max_length=36, null=True),
        ),
    ]
