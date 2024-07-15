from .execute import run_command

def restart():
    op = run_command('venv/bin/python manage.py check')
    if 'System check identified no issues' in op:
        run_command('sudo systemctl start apache2')
        return True, 'successful reload'
    return False, op
