import os, sys
if __name__ == '__main__':
    os.system('DISPLAY=:{} scrot /home/team/lotteh/temp/{}'.format(sys.argv[1], sys.argv[2]))
