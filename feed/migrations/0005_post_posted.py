# Generated by Django 4.2.6 on 2023-11-13 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0004_alter_post_feed_alter_post_file_bucket_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='posted',
            field=models.BooleanField(default=False),
        ),
    ]
