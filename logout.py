import re, traceback, requests, json, threading, time, glob, sys
from subprocess import Popen, STDOUT, PIPE
output = ''
def run_command(command):
    cmd = command.split(' ')
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=str("/"))
    time.sleep(2)
    proc.kill()
    return proc.stdout.read().decode("unicode_escape")

def unique(thelist):
    u = []
    for i in thelist:
        if i not in u: u.append(i)
    return u

logpath = glob.glob('/var/log/auth.log')[-1]

def load_path():
    global output
    output = output + run_command('tail -n 500 {}'.format(logpath))

thread_started = False
load_path()
IPV4SEG  = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = r'(?:(?:' + IPV4SEG + r'\.){3,3}' + IPV4SEG + r')'
IPV6SEG  = r'(?:(?:[0-9a-fA-F]){1,4})'
IPV6GROUPS = (
    r'(?:' + IPV6SEG + r':){7,7}' + IPV6SEG,                  # 1:2:3:4:5:6:7:8
    r'(?:' + IPV6SEG + r':){1,7}:',                           # 1::                                 1:2:3:4:5:6:7::
    r'(?:' + IPV6SEG + r':){1,6}:' + IPV6SEG,                 # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
    r'(?:' + IPV6SEG + r':){1,5}(?::' + IPV6SEG + r'){1,2}',  # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
    r'(?:' + IPV6SEG + r':){1,4}(?::' + IPV6SEG + r'){1,3}',  # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
    r'(?:' + IPV6SEG + r':){1,3}(?::' + IPV6SEG + r'){1,4}',  # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
    r'(?:' + IPV6SEG + r':){1,2}(?::' + IPV6SEG + r'){1,5}',  # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
    IPV6SEG + r':(?:(?::' + IPV6SEG + r'){1,6})',             # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
    r':(?:(?::' + IPV6SEG + r'){1,7}|:)',                     # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::
    r'fe80:(?::' + IPV6SEG + r'){0,4}%[0-9a-zA-Z]{1,}',       # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
    r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,     # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv>
    r'(?:' + IPV6SEG + r':){1,4}:[^\s:]' + IPV4ADDR,          # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
)
IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])  # Reverse rows for greedy match
ips = []
while len(ips) == 0:
    print('awaiting output')
    time.sleep(3)
    if not output and not thread_started:
        thread_started = True
        load_path()
    if output:
        op = output.split('\n')
        op.reverse()
        output = '\n'.join(op)
        ips = unique(re.findall(IPV4ADDR + '|' + IPV6ADDR, output))
        if len(ips) == 0 and thread_started: sys.exit(2)

print(output)

print(ips)

if len(ips) == 0:
    if logpath: output2 = run_command('tail -n 500 {}'.format(logpath))
    op = output2.split('\n')
    op.reverse()
    output = '\n'.join(op)
    ips = unique(re.findall(IPV4ADDR + '|' + IPV6ADDR, output))

ip = ips[0]

def thread_function(ip_address):
    global ip
    TIMEOUT_SECONDS = 60 * 5
    t = 0
    login = ShellLogin.objects.create(ip_address=ip_address)
    while True:
        try:
            login = ShellLogin.objects.get(id=login.id)
        except:
            pass
        print('{} {} '.format(login.validated, login.approved))
        if login.validated:
            if not login.approved:
                sys.exit(2)
                run_command('doveadm kick team {}'.format(ip))
            else: sys.exit(0)
        time.sleep(10)
        t = t + 10
        if t > TIMEOUT_SECONDS: sys.exit(2)
    sys.exit(2)

if ip != '127.0.0.1':
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lotteh.settings')
    import django
    django.setup()
    from django.conf import settings
    from requests.auth import HTTPBasicAuth
    from shell.models import ShellLogin
    from security.models import UserIpAddress
    for i in UserIpAddress.objects.filter(ip_address=ip):
        if i.risk_detected:
            sys.exit(2)
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
#    for ip in ips:
#        if not ip == '127.0.0.1' and check_raw_ip_risk(ip, True):
#            run_command('doveadm kick team {}'.format(output))
    ip = ips[0]
    print(ip)
    if ip != '127.0.0.1':
         thread_function(ip)
#        x = threading.Thread(target=thread_function, args=(ip,))
#        x.start()

