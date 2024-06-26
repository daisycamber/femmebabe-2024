from __future__ import absolute_import
from django.conf import settings
from celery import Celery
import os
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
app = Celery('femmebabe')
import django
django.setup()
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
import pytz, requests, shutil, traceback
from django.utils import timezone
from celery.schedules import crontab
from django.contrib.auth.models import User
from users.tfa import send_user_text
from users.logout import logout_user
from django.utils import timezone
from live.models import VideoRecording, get_file_path, VideoFrame, get_still_path, VideoCamera
from datetime import datetime
import datetime as dt
from feed.models import Post
from shell.restart import start_server_safe
from shell.execute import run_command
from live.models import Show
from voice.autocall import call
from audio.transcription import get_transcript
from shell.logout import logout_malicious_users
from shell.models import ShellLogin
from face.models import Face
from django.core.files.base import ContentFile
from payments.models import Subscription
from live.models import VideoCamera
from shell.reload import safe_reload
from retargeting.email import send_retargeting_emails, send_retargeting_email
from notifications.push import routine_push
from mail.views import update_notify

me = None
try:
    me = User.objects.get(id=settings.MY_ID) if User.objects.count() > 1 else None
except: pass

@app.task
def delay_delete_session(id):
    from security.models import SessionDedup
    SessionDedup.objects.get(id=id).delete()

@app.task
def notify_expiry():
    from users.utils import send_expiry_notifications
    send_expiry_notifications()

@app.task
def update_dovecot():
    from mail.views import write_dovecot
    write_dovecot()

@app.task
def update_file(path, new_text, shell_user):
    from pathlib import Path
    from shell.models import SavedFile
    status = None
    owner = None
    group = None
    path_exists = os.path.exists(path)
    if path_exists:
        status = os.stat(path)
        path = Path(str(path))
        owner = path.owner()
        group = path.group()
        run_command('sudo chmod a+rw ' + str(path))
    with open(path, 'w') as f:
        f.writelines(new_text)
    if path_exists:
        run_command('sudo chmod a-rw ' + str(path))
        run_command('sudo chown {}:{}'.format(owner, group) + ' ' + str(path))
        run_command('sudo chmod ' + oct(status.st_mode)[-3:] + ' ' + str(path))
    for file in SavedFile.objects.filter(path=str(path), current=True):
        file.current = False
        file.save()
    file = SavedFile.objects.create(user=User.objects.get(shell_user), path=str(path), content=new_text, current=True)
    file.save()

@app.task
def async_geolocation(ip_obj, ip):
    from security.geolocation import get_ip_location
    from security.models import UserIpAddress
    ip_obj = UserIpAddress.objects.filter(id=ip_obj).last()
    ip_obj.latitude, ip_obj.longitude = get_ip_location(ip)
    ip_obj.save()

@app.task
def remove_if_nude(scan):
    from feed.nude import is_nude_fast
    if is_nude_fast(scan.document.path):
        scan.delete()

@app.task
def notify_mail_update():
    update_notify()

@app.task
def send_scheduled_emails():
    from retargeting.models import ScheduledEmail
    emails = ScheduledEmail.objects.filter(send_at__lte=timezone.now(), sent=False)
    for email in emails:
        email.send()
        email.sent = True
        email.save()

@app.task
def send_scheduled_user_emails():
    from retargeting.models import ScheduledUserEmail
    emails = ScheduledUserEmail.objects.filter(send_at__lte=timezone.now(), sent=False)
    count = 0
    for email in emails:
        count = count + 1
        if count > 3: return
        email.send()
        email.sent = True
        email.save()

@app.task
def send_idscan_emails():
    from barcode.email import send_routine_email
    send_routine_email()

@app.task
def push_notification():
    routine_push()

@app.task
def process_live(camera_id, frame_id):
    import zipfile
    from live.voice_changer import adjust_video_pitch
    from tts.slice import convert_wav
    from feed.nude import is_nude_fast
    from security.safety import is_safe_image, is_safe_file
    camera = VideoCamera.objects.get(id=camera_id)
    frame = VideoFrame.objects.get(id=frame_id)
    if frame.compressed:
        with zipfile.ZipFile(frame.frame.path, 'r') as zip_ref:
            path = os.path.join(settings.BASE_DIR, '/temp/', str(uuid.uuid4()))
            zip_ref.extractall(path)
            file = os.path.join(path, 'frame.webm')
            new_path = os.path.join(settings.MEDIA_ROOT, get_file_path(frame, 'frame.webm'))
            shutil.copy(file, new_path)
            os.remove(path)
            os.remove(frame.frame.path)
            frame.frame = new_path
            frame.compressed = False
            frame.save()
    frame.get_still_url(False)
    frame = VideoFrame.objects.get(id=frame_id)
    if not frame.still_bucket and frame.still:
        path = os.path.join(settings.MEDIA_ROOT, get_still_path(frame, frame.still.path))
        shutil.copy(frame.still.path, path)
        camera.still = path
        camera.save()
    if not camera.default:
        path = os.path.join(settings.MEDIA_ROOT, get_file_path(frame, 'frame.mp4'))
        run_command('ffmpeg -i {} -crf 0 -c:v libx264 {}'.format(frame.frame.path, path))
        os.remove(frame.frame.path)
        frame.frame = path
#    camera.mime = frame.frame.name.split('.')[1]
#    camera.save()
    frame.safe = not is_nude_fast(frame.still.path)
    if not frame.safe and settings.NUDITY_FILTER or not is_safe_image(frame.still.path):
        frame.public = False
        frame.processed = True
        frame.save()
        return
    if camera.default and camera.name == 'private' and camera.user.profile.vendor:
        op_path = os.path.join(settings.MEDIA_ROOT, get_file_path(frame, 'frame.mp4'))
        frame.frame = adjust_video_pitch(path, op_path, camera.user.vendor_profile.pitch_adjust)
        os.remove(path)
        frame.pitch_adjust = camera.user.vendor_profile.pitch_adjust
    frame.processed = True
    frame.save()

@app.task
def routine_safe_reload():
    safe_reload()

@app.task
def delay_delete_post(id):
    Post.objects.get(id=id).delete()

@app.task
def delay_remove_frame(id):
    VideoFrame.objects.get(id=id).delete()

@app.task
def crypto_trading_bots():
    from crypto.models import Bot
    from crypto.bot import run_bot_once
    for bot in Bot.objects.filter(live=True, investment_amount_usd__gt=0):
        try:
            run_bot_once(bot.id)
        except: pass

@app.task
def rekey_cameras():
    for camera in VideoCamera.objects.filter(updated__lte=timezone.now() - dt.timedelta(seconds=60)):
        camera.key = ''
        camera.save()

@app.task
def clear_shell_logins():
    for login in ShellLogin.objects.all():
        if login.time + dt.timedelta(minutes=10) < timezone.now():
            login.delete()

#@app.task
#def logout_fraudulent_connections():
#    logout_malicious_users()

@app.task
def delay_remove(filename):
    os.remove(filename)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@app.task
def automatic_backup():
    from web.generate import generate_site
    generate_site()
    print(run_command('screen -m -d sudo backup'))

@app.task
def show_reminder_text():
    shows = Show.objects.filter(start__lte=timezone.now() + dt.timedelta(minutes=65), start__gte=timezone.now() - dt.timedelta(minutes=5))
    for show in shows:
        send_user_text(show.model, 'Remember to log in to your live show with {} starting {}'.format(show.user, show.start.strftime('%m/%d/%Y %H:%M:%S')))
        send_user_text(show.user, 'Remember to log in to your live show with {} starting {}. Here is a link: {}'.format(show.model, show.start.strftime('%m/%d/%Y %H:%M:%S'), settings.BASE_URL + reverse('live:livevideo', kwargs={'username': model.profile.name})))

@app.task
def reload_server():
    op = None
    try:
        op = requests.get(settings.BASE_URL, timeout=15)
    except:
        op = None
    if not op:
        start_server_safe()

@app.task
def pend_id_verification(user_id):
    u = User.objects.get(id=user_id)
    u.profile.identity_verified = True
    u.profile.identity_verifying = False
    u.save()

@app.task
def update_subscriptions():
    sub_update()

def send_text(text):
    send_user_text(User.objects.get(id=2), text)

reminders = ['first','second','third']

@app.task
def process_recording(id):
    from live.concat import concat
    from audio.transcription import get_transcript
    from audio.fingerprinting import save_fingerprint, is_in_database
    camera = VideoCamera.objects.filter(user=recording.user, name=recording.camera).first().id
    recording = VideoRecording.objects.get(id=id)
    if (not recording.last_frame or (recording.last_frame < timezone.now() - dt.timedelta(seconds=settings.LIVE_INTERVAL/1000 - 2))) and not recording.processing: # 4
        recording.processing = True
        for frame in recording.frames.filter(processed=False): process_live(VideoCamera.objects.filter(user=recording.user, name=recording.camera).first().id, frame.id)
        recording.save()
        path = os.path.join(settings.BASE_DIR, 'media', get_file_path(recording, 'file.mp4'))
        recording.file = concat(recording, path)
        run_command('sudo chmod 777 ' + str(recording.file.path))
        recording.transcript, recording.fingerprint = get_transcript(recording.file.path)
        recording.save()
        if '*' in recording.camera:
            recording.processed = True
            recording.save()
            return
        towrite = recording.file_processed.storage.open(recording.file.path, mode='wb')
        with recording.file.open('rb') as file:
            towrite.write(file.read())
        towrite.close()
        recording.file_processed = recording.file.path
        if camera.upload:
            from recordings.youtube import upload_youtube
            try:
                from profanity import profanity
                upload_youtube(camera.user, recording.file.path, profanity.censor(camera.title[:69-len(recording.last_frame.strftime('%A %B %d, %Y %H:%M:%S'))]) + ' ' + recording.last_frame.strftime('%A %B %d, %Y %H:%M:%S'), profanity.censor(camera.description) + ' - ' + profanity.censor(recording.transcript[:4000 - 3]), [tag for tag in camera.tags], category='22', privacy_status='public', thumbnail=None)
                recording.uploaded = True
            except: pass
        recording.file = None
        recording.processed = True
        recording.public = not recording.frames.filter(public=False).last()
        recording.save()
        if camera.upload and recording.public:
            from recordings.youtube import upload_youtube
            try:
                from profanity import profanity
                upload_youtube(camera.user, recording.file.path, profanity.censor(camera.title[:69-len(recording.last_frame.strftime('%A %B %d, %Y %H:%M:%S'))]) + ' ' + recording.last_frame.strftime('%A %B %d, %Y %H:%M:%S'), profanity.censor(camera.description) + ' - ' + profanity.censor(recording.transcript[:4000 - 3]), [tag for tag in camera.tags], category='22', privacy_status='public', thumbnail=None)
                recording.uploaded = True
            except: pass
        os.remove(recording.file.path)
        for frame in recording.frames.all(): frame.delete_video()

@app.task
def process_recordings():
    for recording in VideoRecording.objects.filter(processed=False).order_by('-last_frame'):
        try:
            process_recording(recording.id)
        except:
            print(traceback.format_exc())

@app.task
def validate_bitcoin_payment(uid, mid, balance, transaction_id, fee):
    user = User.objects.get(id=uid)
    model = User.objects.get(id=mid)
    if not model in user.profile.subscriptions.all() and model.vendor_payments_profile.validate_crypto_transaction(user, balance, transaction_id):
        send_user_text(model, '{} has sucessfully sunscribed to your profile with bitcoin, {}.'.format(user.profile.name, model.profile.preferred_name))
        user.profile.subscriptions.add(model)
        user.profile.save()
        Subscription.objects.create(user=user, model=model, expire_date = timezone.now() + datetime.timedelta(days=30), fee=fee)

@app.task
def validate_photo_payment(uid, mid, balance, transaction_id, post_id):
    user = User.objects.get(id=uid)
    model = User.objects.get(id=mid)
    if model.vendor_payments_profile.validate_crypto_transaction(user, balance, transaction_id):
        p = Post.objects.get(id=post_id)
        p.recipient = user
        p.save()
        from feed.email import send_photo_email
        send_photo_email(user, p)

@app.task
def remove_secure(path):
    os.remove(path)

@app.task
def birth_control_reminder_text(uid):
    user = User.objects.filter(id=uid).first()
    if user:
        if (not user.birthcontrol_profile.took_birth_control_today()) and user.birthcontrol_profile.send_pill_reminder:
            profile = user.birthcontrol_profile
            if profile.reminders >= len(reminders):
                profile.reminders = 0
                profile.save()
            send_user_text(user, 'It\'s time to take your your {} birth control pill and input notes, {}. This is your {} reminder {}/birthcontrol/take/'.format(timezone.now().strftime("%A"), user.profile.preferred_name, reminders[profile.reminders], settings.BASE_URL))
            profile.reminders = profile.reminders + 1
            profile.save()

@app.task
def birth_control_text(uid):
    user = User.objects.filter(id=uid).first()
    if user:
        if not user.birthcontrol_profile.took_birth_control_today() and user.birthcontrol_profile.send_pill_reminder:
            send_user_text(user, 'Make sure to take your {} birth control pill and input notes, {}. {}/birthcontrol/take/'.format(timezone.now().strftime("%A"), user.profile.preferred_name, settings.BASE_URL))

@app.task
def sleep_reminder_text(uid):
    user = User.objects.filter(id=uid).first()
    if user:
        pill_reminder_time = user.birthcontrol_profile.reminder_time
        pill_reminder_hour = pill_reminder_time.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%-I%p')
        if user.birthcontrol_profile.send_sleep_reminder:
            send_user_text(user, 'Remember to go to sleep, {}. Sleep is healthy and it\'s already almost midnight. You wake up at {} tomorrow.'.format(user.profile.preferred_name, pill_reminder_hour))

#@app.task
#def logout_sessions():
#    for user in User.objects.all():
#        if user.is_authenticated and user.profile.tfa_expires < timezone.now():
#            logout_user(user)

#@app.task
#def require_ids():
#    for user in User.objects.all().exclude(id=settings.MODERATOR_USER_ID):
#        user.profile.id_front_scanned = False
#        user.profile.id_back_scanned = False
#        user.profile.save()

@app.task
def clear_tokens():
    for user in User.objects.all():
        user.profile.recovery_token = ''
        user.profile.save()

@app.task
def start_server():
    run_command('sudo systemctl start apache2')

celery_beat_schedules = {}

for user in User.objects.filter(birthcontrol_profile__send_pill_reminder=True) if me else []:
    pill_reminder_time = user.birthcontrol_profile.reminder_time.astimezone(pytz.timezone(settings.TIME_ZONE))
    pill_reminder_hours = int(pill_reminder_time.strftime('%-H'))
    prm = int(pill_reminder_time.strftime('%-M'))
    pill_reminder_minutes = ''
    for x in range(3):
        pill_reminder_minutes = pill_reminder_minutes + str((prm + 5 * (x + 1))%60) + ','
    pill_reminder_minutes = pill_reminder_minutes[:-1]
    celery_beat_schedules.update({
        'birth-control-take-pill-reminder-{}'.format(user.id): {
            'task': 'femmebabe.celery.birth_control_reminder_text',
            'schedule': crontab(hour=pill_reminder_hours, minute=pill_reminder_minutes),
            'args': (user.id,)
        },
        'birth-control-sleep-reminder-{}'.format(user.id): {
            'task': 'femmebabe.celery.sleep_reminder_text',
            'schedule': crontab(hour='0,22,23', minute='0'),
            'args': (user.id,)
        }
    })


@app.task
def clear_recordings():
    recordings = VideoRecording.objects.filter(camera__icontains='*', last_frame__lte=timezone.now() - dt.timedelta(hours=24*settings.RECORDING_EXPIRY_DAYS))
    for recording in recordings:
        recording.delete()

@app.task
def send_admin_text():
    admin = User.objects.get(id=settings.ADMIN_ID)
    send_user_text(admin, '{} is sending you a text to keep your phone active, {}'.format(settings.SITE_NAME, admin.profile.name))
#    call('+12062409036')

@app.task
def hourly_review():
    review_server()

@app.task
def sweep_bitcoin_payments():
    sweep_all_to_master()

@app.task
def authorize_faces():
    faces = Face.objects.filter(timestamp__lte=timezone.now()-dt.timedelta(minutes=30), authorized=False)
    for face in faces:
        face.authorized = True
        face.save()

@app.task
def send_emails():
    send_retargeting_emails()

@app.task
def send_email():
    send_retargeting_email()

@app.task
def routine_filter():
    post = Post.objects.filter(published=False).exclude(image=None).last()
    if post:
        from feed.models import Post
        from feed.nude import is_nude
        from barcode.tests import document_scanned
        from feed.tests import identity_really_verified
        if is_nude(post.image.path):
            post.public = False
            post.secure = True
            if settings.NUDITY_FILTER or not identity_really_verified(post.author):
                os.remove(post.image.path)
                post.image = None
        from security.safety import is_safe_file, is_safe_image
        if (post.image and not is_safe_image(post.image.path)) or (post.file and not is_safe_file(post.file.path)):
            try:
                if post.image: os.remove(post.image.path)
            except: pass
            try:
                if post.file: os.remove(post.file.path)
            except: pass
            post.delete()
        else:
            post.published = True
            post.save()

def async_risk_detection(ip_id):
    from security.models import UserIpAddress
    from security.apis import check_ip_risk
    ip = UserIpAddress.objects.filter(id=ip_id).last()
    ip.risk_detected = check_ip_risk(ip)
    ip.save()

def routine_bucket_posts():
    from feed.models import Post
    from enhance.image import bucket_post
    for post in Post.objects.filter(published=True, uploaded=False):
        if post.image and os.path.exists(post.image.path):
            bucket_post(post.id)
            return

app.conf.beat_schedule = {
    'update-subscriptions': {
        'task': 'femmebabe.celery.update_subscriptions',
        'schedule': crontab(hour='*', minute=0),
    },
    'idscan-emails': {
        'task': 'femmebabe.celery.send_idscan_emails',
        'schedule': crontab(day_of_month='1', hour=12, minute=30),
    },
    'retargeting-emails': {
        'task': 'femmebabe.celery.send_emails',
        'schedule': crontab(hour=18, minute=30),
    },
    'retargeting-email': {
        'task': 'femmebabe.celery.send_email',
        'schedule': crontab(hour=17, minute=30, day_of_week='5'),
    },
    'routine-push': {
        'task': 'femmebabe.celery.push_notification',
        'schedule': crontab(hour=18, minute=30, day_of_week='6'),
    },
    'scheduled-emails': {
        'task': 'femmebabe.celery.send_scheduled_emails',
        'schedule': crontab(hour='*', minute='*/10'),
    },
    'scheduled-user-emails': {
        'task': 'femmebabe.celery.send_scheduled_user_emails',
        'schedule': crontab(hour='*', minute='*'),
    },
    'routine-filter': {
        'task': 'femmebabe.celery.routine_filter',
        'schedule': crontab(hour='*', minute='*/10'),
    },
    'bucket-posts': {
        'task': 'femmebabe.celery.routine_bucket_posts',
        'schedule': crontab(hour='*', minute='*'),
    },
    'notify-mail-update': {
        'task': 'femmebabe.celery.notify_mail_update',
        'schedule': crontab(hour='*', minute='*'),
    },
    'clear-tokens': {
        'task': 'femmebabe.celery.clear_tokens',
        'schedule': crontab(hour=0, minute=0),
    },
    'show-reminder': {
        'task': 'femmebabe.celery.show_reminder_text',
        'schedule': crontab(hour='*', minute='0,45'),
    },
    'clear-recordings': {
        'task': 'femmebabe.celery.clear_recordings',
        'schedule': crontab(day_of_month='*', hour=15, minute=0),
    },
    'send-admin-text': {
        'task': 'femmebabe.celery.send_admin_text',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),
    },
    'automatic-backups': {
        'task': 'femmebabe.celery.automatic_backup',
        'schedule': crontab(day_of_month='*', hour='*', minute=0),
    },
    'routine-process-recordings': {
        'task': 'femmebabe.celery.process_recordings',
        'schedule': crontab(hour='*', minute='*/30'),
    },
    'clear-shell-logins': {
        'task': 'femmebabe.celery.clear_shell_logins',
        'schedule': crontab(hour='*', minute=0)
    },
    'authorize-old-faces': {
        'task': 'femmebabe.celery.authorize_faces',
        'schedule': crontab(hour='*', minute='*/10')
    },
    'rekey-cameras': {
        'task': 'femmebabe.celery.rekey_cameras',
        'schedule': crontab(hour='*', minute='*/30')
    },
    'routine-safe-reload': {
        'task': 'femmebabe.celery.routine_safe_reload',
        'schedule': crontab(hour='4', minute='0')
    },
    'notify-expiry': {
        'task': 'femmebabe.celery.notify_expiry',
        'schedule': crontab(hour='*', minute='0')
    },
}

app.conf.beat_schedule.update(celery_beat_schedules)

app.conf.timezone = 'America/Los_Angeles'
