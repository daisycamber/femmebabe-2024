from django import template

register = template.Library()

@register.filter('decryptit')
def decryptit(input):
    from security.crypto import decrypt
    return decrypt(input)

@register.filter('encryptit')
def encryptit(input):
    from security.crypto import encrypt
    return encrypt(input)