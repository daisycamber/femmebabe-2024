ONE = ['happy', 'sexy', 'fun', 'beautiful', 'pretty', 'handsome', 'dirty', 'gorgeous', 'stunning', 'lovely', 'perfect', 'busty', 'famous', 'best', 'lovely', 'stunning']
TWO = ['person', 'woman', 'girl', 'beauty', 'sweetheart', 'lover', 'fox', 'bear', 'cutie', 'beast', 'babe', 'bestie', 'legend']

from django.contrib.auth.models import User
import random

TRIES = (len(ONE)-1) * (len(TWO)-1) * 100

def generate_username():
    username = None
    tries = 0
    while not username:
        username = ONE[random.randrange(0, len(ONE)-1)] + TWO[random.randrange(0, len(TWO)-1)] + str(random.randrange(0, 99))
        tries = tries + 1
        if tries > TRIES: break
        if User.objects.filter(username=username).count() == 0:
            return username
    return 'Guest' + str(random.randrange(100000, 999999))
