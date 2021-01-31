import evdev

import emit
from key import key

# the name of the device to grab
def device():
    return "/dev/input/event0"

# the remapping table
def keytab():
    return {
        evdev.ecodes.KEY_CAPSLOCK : leftctrl(),
    }

class leftctrl(key):
    """ a ctrl key.  if pressed solo emit a C-g. """
    def __init__(self):
        super().__init__(passthrough=False)
    def keysolo(self):
        emit.keydown(evdev.ecodes.KEY_LEFTCTRL)
        emit.keypress(evdev.ecodes.KEY_G)
        emit.keyup(evdev.ecodes.KEY_LEFTCTRL)
    def _keydown(self):
        emit.keydown(evdev.ecodes.KEY_LEFTCTRL)
    def _keyxcape(self, event):
        # the `key` was xcaped.  that is, another key was pressed while this key
        # was held down (see _k/kmod). this will be interpreted as
        # CTRL+event.code
        emit.passthrough(event)
    def _keyup(self):
        emit.keyup(evdev.ecodes.KEY_LEFTCTRL)
