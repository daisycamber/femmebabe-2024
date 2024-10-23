import re
import os
import sys
import select
import paramiko
import time
from django.conf import settings
from threading import local

retry_time = 60 * 2

host_ip = '127.0.0.1'
host_port = 22
ssh = None
ssh_session = None
channel = None
stdin = None
stdout = None

def connect():
    ssh = None
    i = 0
    while True:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client = paramiko.SSHClient()
            pkey = paramiko.RSAKey.from_private_key_file("/home/{}/.ssh/id_rsa".format(settings.BASH_USER))
            ssh.connect(host_ip, port=host_port, username=settings.BASH_USER, password=settings.BASH_USER, pkey=pkey)
            break
        except paramiko.AuthenticationException:
            print("Authentication failed when connecting to %s" % host_ip)
            sys.exit(1)
        except:
            print("Could not SSH to %s, waiting for it to start" % host_ip)
            i += 1
            time.sleep(2)
            # If we could not connect within time limit
            if i >= retry_time:
                print("Could not connect to %s. Giving up" % host_ip)
                return None
    global stdin
    global stdout
    global channel
    channel = ssh.invoke_shell(width=1000, height=1000)
    stdin = channel.makefile('wb')
    stdout = channel.makefile('rb')

def shell_fix(input):
    return re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', input).replace('\b', '').replace('\r', '')

def run_command(command):
    global channel
    global ssh
    global stdin
    global stdout
    try:
        if channel == None:
            connect()
            print('connect')
    except:
        connect()
    output = ""

    channel.send(command + '\n')

    while not channel.recv_ready():
        time.sleep(1)

    read = True
    while read:
        read = False
        if channel.recv_ready():
            rl, wl, xl = select.select([ channel ], [ ], [ ], 0.0)
            if len(rl) > 0:
                tmp = channel.recv(999999999)
                output = output + tmp.decode()
                read = True
                time.sleep(1)
    return shell_fix(output) #.decode('ascii'))
