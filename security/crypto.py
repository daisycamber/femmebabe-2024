import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from Crypto import Random
from django.conf import settings
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

def decode_hex_string(encoded_string):
    bytes_data = bytes.fromhex(encoded_string[1:])
    decoded_string = bytes_data.decode('utf-8', 'ignore')
    return decoded_string

def btoa(value: str) -> str:
    # btoa source: https://github.com/WebKit/WebKit/blob/fcd2b898ec08eb8b922ff1a60adda7436a9e71de/Source/JavaScriptCore/jsc.cpp#L1419
    binary = value.encode("latin-1")
    return b64encode(binary).decode()

def atob(value: str) -> str:
    binary = b64decode(value.encode())
    return binary.decode("latin-1")

def encrypt(raw, secret=None):
    key = settings.AES_KEY #Must Be 16 char for AES128
    if secret: key = secret
    raw = pad(raw.encode(),16)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(raw)).decode("utf-8")

def decrypt(raw, secret=None):
    key = settings.AES_KEY #Must Be 16 char for AES128
    if secret: key = secret
    raw = raw.replace(' ', '+')
    enc = pad(raw.encode(),16)
    try:
        enc = base64.b64decode(enc)
    except:
        enc = base64.urlsafe_b64decode(enc)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
    return unpad(cipher.decrypt(enc), 16).decode("utf-8")

def encrypt_cbc(data, secret=None):
    key = settings.AES_KEY #Must Be 16 char for AES128
    if secret: key = secret
    data = pad(base64.b64encode(data.encode()).decode('utf-8').encode(),16)
    iv = get_random_bytes(16)
    cipher = AES.new(key.encode('utf-8'),AES.MODE_CBC,iv)
#    print('random IV : ' , base64.b64encode(cipher.iv).decode('utf-8'))
#    print(base64.b64encode(cipher.iv).decode('utf-8'))
    return base64.b64encode(cipher.iv).decode('utf-8') + base64.b64encode(cipher.encrypt(data)).decode('utf-8')

def decrypt_cbc(raw, secret=None):
    key = settings.AES_KEY #Must Be 16 char for AES128
    if secret: key = secret
    raw = raw.replace(' ', '+')
    iv = raw[:24]
    raw = pad(raw[24:].encode(), 16)
    try:
        enc = base64.b64decode(raw)
    except:
        enc = base64.urlsafe_b64decode(raw)
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, base64.b64decode(iv))
    enc = base64.b64decode(unpad(cipher.decrypt(enc), 16).decode('utf-8')).decode('utf-8')
    print(enc)
    return enc #base64.b64decode(enc).decode('utf-8')
