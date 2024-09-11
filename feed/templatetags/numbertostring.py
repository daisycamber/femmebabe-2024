import math
n = ['one','two','three','four','five', 'six', 'seven', 'eight', 'nine', 'ten']
tn = ['eleven','twelve','thir','four','fif','six','seven','eigh','nine']
nn = ['ten','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
def number_to_string(num):
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
        return n[math.floor(num/100)-1]+'-hundred-'+nn[math.floor((num%100)/10)-1]+extra
    if num < 10000:
        extra = '-'+n[num%10-1]
        if num%10 == 0:
            extra = ''
        return n[math.floor(num/1000)-1] + '-thousand-' + n[math.floor(num/1000)-1]+'-hundred-'+nn[math.floor((num%100)/10)-1]+extra
    return 'number too large to compute!'

#for x in range(1,10000):
#    print(number_to_string(x))

