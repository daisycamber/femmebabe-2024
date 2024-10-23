from shell.execute import run_command
from subprocess import check_output
from django.conf import settings
import os

def get_logs():
    check_output(['sudo', 'chmod', '-R', 'a+rX', '/var/log/apache2/'])
    return check_output(['sh', str(os.path.join(settings.BASE_DIR, 'errors/logs.sh'))]).decode('unicode_escape')
