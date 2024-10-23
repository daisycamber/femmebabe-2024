import re

def process(data):
    data = data.encode("unicode_escape").decode("utf-8")
    split = data.split('\\')
    output = ''
    for s in split:
        output = output + s[4:] + ' '
    return output
