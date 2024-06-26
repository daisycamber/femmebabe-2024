# Generated by Django 4.2.5 on 2023-10-04 16:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import voice.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.TextField(blank=True, default='', null=True)),
                ('number', models.IntegerField(blank=True, default=1, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VoiceProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_call', models.DateTimeField(blank=True, default=None, null=True)),
                ('recordings', models.BooleanField(default=False)),
                ('interactive', models.TextField(blank=True, default='', null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='voice_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sid', models.TextField(blank=True, default='', null=True)),
                ('call_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='calls', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserChoice',
            fields=[
                ('choice_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='voice.choice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voice_choices', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('voice.choice',),
        ),
        migrations.CreateModel(
            name='AudioInteractive',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.TextField(blank=True, default='', null=True)),
                ('interactive', models.TextField(blank=True, default='', null=True)),
                ('content', models.FileField(blank=True, null=True, upload_to=voice.models.get_file_path)),
                ('uploaded_file', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('choices', models.ManyToManyField(blank=True, to='voice.userchoice')),
            ],
        ),
    ]
