from subprocess import Popen, STDOUT, PIPE
from django.conf import settings
from threading import Timer

banned_commands = ['rm']

timeout_sec = 20

def run_command_timeout(command):
    cmd = command.split(' ')
    if cmd[0] in banned_commands:
        return 'command not accepted.\n'
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=str(settings.BASE_DIR))
    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
    finally:
        timer.cancel()
    return proc.stdout.read().decode("unicode_escape")
