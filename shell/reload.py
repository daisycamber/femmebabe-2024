from .execute_timeout import run_command_timeout
from .execute import run_command
from threading import Thread
from time import sleep

def safe_reload():
    done, op = reload()
    if done:
        return op
    return 'reload failed, output - {}\n'.format(op)

def reload_thread():
    sleep(3)
    run_command('sudo systemctl restart daphne')
    run_command('sudo systemctl reload apache2 && sudo systemctl restart apache2')

def reload():
    op = run_command_timeout('venv/bin/python manage.py check')
    if 'System check identified no issues' in op:
        thread = Thread(target=reload_thread)
        thread.start()
        return True, 'successful reload\n'
    return False, op
