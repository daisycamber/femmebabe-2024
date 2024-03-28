import math
n = ['one','two','three','four','five', 'six', 'seven', 'eight', 'nine', 'ten']
tn = ['eleven','twelve','thir','four','fif','six','seven','eigh','nine']
nn = ['ten','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']

def nts(num):
    if not isinstance(num, int):
        num = int(num) if num != '' else 'no'
    if num == 0:
        return 'no'
    return number_to_string(num)

def number_to_string(num, default=''):
    if not isinstance(num, int):
        num = int(num) if num != '' else 'no'
    if num == 0:
        return default
    if num < 11:
        return n[num-1]
    if num < 20:
        if num < 13:
            return tn[num-11]
        return tn[num-11] + 'teen'
    if num < 100:
        extra = '-'+n[num%10-1]
        if num%10 == 0:
            extra = ''
        return nn[math.floor(num/10)-1]+extra
    if num < 1000:
        extra = '-'+n[num%10-1]
        if num%10 == 0:
            extra = ''
        snum = str(num)
        return n[math.floor(num/100)-1]+'-hundred'+ ('-' if number_to_string(int(snum[1:])) != default else '') + (number_to_string(int(snum[1:])) if number_to_string(int(snum[1:])) != default else '')
    if num < 10000:
        snum = str(num)
        return number_to_string(int(snum[:1])) + '-thousand' + ('-' if number_to_string(int(snum[1:])) != '' else '') +number_to_string(int(snum[1:]))
    if num < 100000:
        snum = str(num)
        return number_to_string(int(snum[:2])) + '-thousand' + ('-' if number_to_string(int(snum[2:])) != '' else '') + number_to_string(int(snum[2:]))
    if num < 1000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 3]) + '-thousand' + ('-' if number_to_string(snum[len(snum)-3:]) != '' else '') + number_to_string(snum[len(snum)-3:])
    if num < 1000000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 6]) + '-million' + ('-' if number_to_string(snum[len(snum)-6:]) != '' else '') + number_to_string(snum[len(snum)-6:])
    if num < 1000000000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 9]) + '-billion' + ('-' if number_to_string(snum[len(snum)-9:]) != '' else '') + number_to_string(snum[len(snum)-9:])
    if num < 1000000000000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 12]) + '-trillion' + ('-' if number_to_string(snum[len(snum)-12:]) != '' else '') + number_to_string(snum[len(snum)-12:])
    if num < 1000000000000000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 15]) + '-quadrillion' + ('-' if number_to_string(snum[len(snum)-15:]) != '' else '') + number_to_string(snum[len(snum)-15:])
    if num < 1000000000000000000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 18]) + '-quintrillion' + ('-' if number_to_string(snum[len(snum)-18:]) != '' else '') + number_to_string(snum[len(snum)-18:])
    if num < 1000000000000000000000000:
        snum = str(num)
        return number_to_string(snum[:len(snum) - 21]) + '-sextillion' + ('-' if number_to_string(snum[len(snum)-21:]) != '' else '') + number_to_string(snum[len(snum)-21:])
    return 'number too large to compute!'
