# Generated by Django 5.0.1 on 2024-03-09 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audio', '0002_audiorecording_pitches_audiorecording_volumes'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiorecording',
            name='pitch_notes',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
