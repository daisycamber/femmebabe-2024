import re, traceback, requests, json, threading, time
from django.conf import settings
from requests.auth import HTTPBasicAuth
from subprocess import Popen, STDOUT, PIPE
from shell.models import ShellLogin
FRAUDGUARD_USER = settings.FRAUDGUARD_USER
FRAUDGUARD_SECRET = settings.FRAUDGUARD_SECRET
RISK_LEVEL = 1

def run_command(command):
    cmd = command.split(' ')
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=str(settings.BASE_DIR))
    proc.wait()
    return proc.stdout.read().decode("unicode_escape")

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

def unique(list):
    u = []
    for i in list:
        if i not in u: u.append(i)
    return u

def logout_malicious_users():
    output = run_command('sudo tail -500 /var/log/auth.log')
    ips = unique(re.findall('Accepted publickey for ' + settings.BASH_USER + ' from ([\d]+\.[\d]+\.[\d]+\.[\d]+)', output))
    for ip in ips:
        if not ip == '127.0.0.1' and check_raw_ip_risk(ip, True):
            run_command('doveadm kick {} {}'.format(settings.BASH_USER, output))
