# Generated by Django 5.0.7 on 2024-09-04 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0022_historicaluseripaddress_last_updated_sun_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluseripaddress',
            name='risk_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='useripaddress',
            name='risk_count',
            field=models.IntegerField(default=0),
        ),
    ]
