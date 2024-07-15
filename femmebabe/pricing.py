def get_zeroes(length):
    z = ''
    for x in range(int(length)): z = z + '0'
    return z

def get_pricing_options(length=54):
    tickets = []
    tickets_per_deca = 4
    t = [25,50,75,100,200]
    for x in range(0, 5):
        tickets = tickets + [str(t[x])]
    for x in range(5, int(length)):
        tickets = tickets + [str(t[x%5]) + get_zeroes(int(x/5))]
    return [5,10,15,20] + tickets
