import evdev

_ui = None

def setui(ui):
    global _ui
    _ui = ui

def passthrough(event):
    _ui.write(event.type, event.code, event.value)

def keyevent(keycode, evalue):
    _ui.write(evdev.ecodes.EV_KEY, keycode, evalue)

# --

def keydown(keycode):
    keyevent(keycode, 1)

def keyup(keycode):
    keyevent(keycode, 0)

def keypress(keycode):
    keydown(keycode)
    keyup(keycode)
