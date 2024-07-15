import re, traceback, requests, json
with open('/etc/apis.json') as config_file:
    keys = json.load(config_file)
from subprocess import Popen, STDOUT, PIPE
def run_command(command):
    cmd = command.split(' ')
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=str("/"))
    proc.wait()
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
import glob
output = run_command('tail -n 500 {}'.format(glob.glob('/var/log/auth.log*')[-1]))
print(output)
op = output.split('\n')
op.reverse()
output = '\n'.join(op)
ips = unique(re.findall('Accepted publickey for team from ([\d]+\.[\d]+\.[\d]+\.[\d]+)', output))
if len(ips) == 0:
    import sys
    sys.exit(0)
ip = ips[0]
if ip != '127.0.0.1':
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
    ip = ips[0]
