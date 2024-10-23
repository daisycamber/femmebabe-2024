
ltr = 300

def get_logs():
    output = ''
    with open('/var/log/apache2/error.log', 'r') as f:
        for x in range(10):
            output = output + f.readlines()[-(x)] + '\n'
    return output
