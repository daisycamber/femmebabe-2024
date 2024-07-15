from django.conf import settings
banned_commands = ['rm']

def run_command(command):
    from subprocess import Popen, STDOUT, PIPE
    cmd = command.split(' ')
    if cmd[0] in banned_commands:
        return 'command not accepted.\n'
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=str(settings.BASE_DIR))
    proc.wait()
    return proc.stdout.read().decode("unicode_escape")
