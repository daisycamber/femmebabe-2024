import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from django.conf import settings

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
    return unpad(cipher.decrypt(enc),16).decode("utf-8")

#encrypted = encrypt(data)
#print('encrypted ECB Base64:',encrypted.decode("utf-8", "ignore"))

#decrypted = decrypt(encrypted)
#print('data: ',decrypted.decode("utf-8", "ignore"))
