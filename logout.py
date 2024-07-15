import re, traceback, requests, json, threading, time
from subprocess import Popen, STDOUT, PIPE

def run_command(command):
    cmd = command.split(' ')
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=str("/home/"))
    proc.wait()
    return proc.stdout.read().decode("unicode_escape")

def unique(thelist):
    u = []
    for i in thelist:
        if i not in u: u.append(i)
    return u

output = run_command('sudo tail -n 500 /var/log/auth.log*')
op = output.split('\n')
op.reverse()
output = '\n'.join(op)
ips = unique(re.findall('Accepted publickey for team from ([\d]+\.[\d]+\.[\d]+\.[\d]+)', output))
print(ips)

ip = ips[0]

def thread_function(ip_address):
    global ip
    login = ShellLogin.objects.create(ip_address=ip_address)
    while not login.approved:
        try:
            login = ShellLogin.objects.get(id=login.id)
        except:
            pass
        time.sleep(10)
        if (not login.approved) and login.validated:
            run_command('doveadm kick team {}'.format(ip))
            raise Exception

if ip != '127.0.0.1':
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'femmebabe.settings')
    import django
    django.setup()
    from django.conf import settings
    from requests.auth import HTTPBasicAuth
    from shell.models import ShellLogin
    FRAUDGUARD_USER = settings.FRAUDGUARD_USER
    FRAUDGUARD_SECRET = settings.FRAUDGUARD_SECRET
    RISK_LEVEL = 1
    def check_raw_ip_risk(ip_addr, soft=False):
        try:
            ip=requests.get('https://api.fraudguard.io/ip/' + ip_addr, verify=True, auth=HTTPBasicAuth(FRAUDGUARD_USER, FRAUDGUARD_SECRET))
            j = ip.json()
            if int(j['risk_level']) > RISK_LEVEL:
                return True
            else:
                return False
        except:
            print(traceback.format_exc())
            return not soft
        return False
    for ip in ips:
        if not ip == '127.0.0.1' and check_raw_ip_risk(ip, True):
            run_command('doveadm kick team {}'.format(output))
    ip = ips[0]
    print(ip)
    if ip != '127.0.0.1':
        x = threading.Thread(target=thread_function, args=(ip,))
        x.start()
