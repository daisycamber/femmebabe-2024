from bitcoinlib.wallets import Wallet, wallet_create_or_open
import sys
from django.utils.crypto import get_random_string

args = sys.argv
arg = args[1]

name = get_random_string(length=16)

if arg == 'create':
    w = Wallet.create(name=name)
    key1 = w.get_key()
    print(key1.address + ',' + key1.wif)
elif arg == 'balance':
    w = Wallet.create(name=name, keys=args[2])
    w.scan()
    print(w.balance())
elif arg == 'info':
    w = wallet_create_or_open(name=name, keys=args[2])
    w.scan()
    print(w.info())
elif arg == 'send':
    keys = args[2].split(',')
    w = wallet_create_or_open(name=name, keys=keys)
    w.scan()
    w.utxos_update()
    t = w.send_to(args[3], args[4] + ' BTC', offline=False)
    print(t.info())
