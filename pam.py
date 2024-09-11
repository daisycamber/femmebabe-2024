import re, traceback, requests, json, regex, sys, glob, time, threading, datetime, asyncio
with open('/etc/apis.json') as config_file:
    keys = json.load(config_file)
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

def check_blacklist(ip):
    try:
        with open('blacklist.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.replace('\n', '') == ip: return True
        return False
    except: pass
    return False

def blacklist(ip):
    with open('blacklist.txt', 'a') as file:
        file.write('{}\n'.format(ip))
        file.close()

logpath = glob.glob('/var/log/auth.log')[-1]

def load_path1():
    global output
#    print(output)

def load_path2():
    global output
    output = run_command('tail -n 500 {}'.format(logpath))

thread_started = False
#load_path1()
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
    r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,     # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r'(?:' + IPV6SEG + r':){1,4}:[^\s:]' + IPV4ADDR,          # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
)
IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])  # Reverse rows for greedy match
#output = run_command('tail -n 500 {}'.format(logpath1))

ips = []
#while not output:
#    print('awaiting output')
#    time.sleep(3)
#    if not output and not thread_started:
#        thread_started = True
#        load_path2()
#    if output:
#        op = output.split('\n')
#        op.reverse()
#        output = '\n'.join(op)
#        ips = unique(re.findall(IPV4ADDR + '|' + IPV6ADDR, output))
#        if len(ips) == 0 and thread_started: sys.exit(2)

#print(output)

#print(ips)
if len(ips) == 0:
    if logpath: output2 = run_command('tail -n 500 {}'.format(logpath))
    op = output2.split('\n')
    op.reverse()
    output = '\n'.join(op)
    ips = unique(re.findall(IPV4ADDR + '|' + IPV6ADDR, output))
#if len(ips) == 0:
#    import sys
#    sys.exit(0)
ip = ips[0]
print(ip)
if ip != '127.0.0.1':
    print('Foreign IP')
    import os
    from requests.auth import HTTPBasicAuth
    FRAUDGUARD_USER = keys['FRAUDGUARD_USER']
    FRAUDGUARD_SECRET = keys['FRAUDGUARD_SECRET']
    ANTIDEO_KEY = keys['ANTIDEO_KEY']
    RISK_LEVEL = 1
    def check_raw_ip_risk(ip_addr, soft=False, guard=True):
        if not guard:
            try:
                ip=requests.get('https://api.antideo.com/ip/health/' + ip_addr + '&apiKey={}'.format(ANTIDEO_KEY))
                j = None
                try:
                    j = ip.json()
                except: pass
                if j and j['health']['toxic'] or j['health']['spam']:
                    return True
                else:
                    return not soft
            except:
                print(traceback.format_exc())
                return not soft
        try:
            ip=requests.get('https://api.fraudguard.io/v2/ip/' + ip_addr, verify=True, auth=HTTPBasicAuth(FRAUDGUARD_USER, FRAUDGUARD_SECRET))
            for resp in ip.history: print(resp.status_code)
            print(ip)
            j = ip.json()
            if int(j['risk_level']) > RISK_LEVEL:
                return True
            else:
                return False
        except:
            print(traceback.format_exc())
            return not soft
        return False
    blacklisted = check_blacklist(ip)
    if not ip == '127.0.0.1' and (blacklisted or check_raw_ip_risk(ip, soft=True)):
        run_command('doveadm kick team {}'.format(output))
        if not blacklisted:
            blacklist(ip)
        sys.exit(1)
    print(blacklisted)
    sys.exit(0)
    ip = ips[0]
