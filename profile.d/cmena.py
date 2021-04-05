import evdev
import psutil
import subprocess
import sys

import emit
from key import key

def device():
    """return the device to be grabbed by the event loop"""
    return "/dev/input/event0"

def keytab():
    """return a remapping table. a mapping of evdev.ecodes to other ecodes, or
    `key` objects.

    """

    # make KEY_LEFTCTRL emit HYPER (mod3) with the aid of xkb:
    #
    #  1. map KEY_LEFTCTRL into KEY_CAPSLOCK
    #
    #  2. patch /usr/share/X11/xkb/symbols/pc:
    #     --- pc.original  2021-04-04 10:27:19.865794591 -0700
    #     +++ pc           2021-04-04 10:32:44.802757364 -0700
    #     @@ -21,3 +21,3 @@
    #     -    key <CAPS> {       [ Caps_Lock             ]       };
    #     +    key <CAPS> {       [ Hyper_L               ]       };
    #          key <NMLK> {       [ Num_Lock              ]       };
    #     @@ -55,3 +55,3 @@
    #          key <HYPR> {       [ NoSymbol, Hyper_L     ]       };
    #     -    modifier_map Mod4   { <HYPR> };
    #     +    modifier_map Mod3   { <HYPR> };
    #          // End of modifier mappings.

    return {
        evdev.ecodes.KEY_LEFTCTRL   : evdev.ecodes.KEY_CAPSLOCK, # hyper
        evdev.ecodes.KEY_RIGHTCTRL  : evdev.ecodes.KEY_CAPSLOCK, # hyper
        evdev.ecodes.KEY_F1         : volkey(evdev.ecodes.KEY_MUTE),
        evdev.ecodes.KEY_F2         : volkey(evdev.ecodes.KEY_VOLUMEDOWN),
        evdev.ecodes.KEY_F3         : volkey(evdev.ecodes.KEY_VOLUMEUP),
        evdev.ecodes.KEY_RIGHTSHIFT : rightshift(),
        evdev.ecodes.KEY_LEFTSHIFT  : leftshift(),
        evdev.ecodes.KEY_CAPSLOCK   : leftctrl(),
        evdev.ecodes.KEY_LEFTMETA   : leftmeta(),
        evdev.ecodes.KEY_BACKSLASH  : backslash(),
    }


class leftmeta(key):
    """when solo, run rofi - if rofi is running terminate it.  see:
        https://github.com/davatorium/rofi

    """
    @staticmethod
    def rofiproc():
        for p in psutil.process_iter():
            if "rofi" in p.name():
                return p

    def __init__(self):
        super().__init__(passthrough=True)

    def keysolo(self):
        proc = self.rofiproc()
        if proc:
            proc.terminate()
            return
        # --
        subprocess.run(["_rofi"])


class backslash(key):
    """xcape the backlash key.  when pressed solo emit the "\" character on a
    keyup, otherwise act like a meta key. sys.exit() if q is pressed while in
    use as a meta modifier.

    """
    def __init__(self):
        super().__init__(passthrough=False)

    def keysolo(self):
        emit.keypress(evdev.ecodes.KEY_BACKSLASH)

    def _keyxcape(self, event):
        if event.code == evdev.ecodes.KEY_Q:
            sys.exit(0)
        # --
        emit.keydown(evdev.ecodes.KEY_LEFTMETA)
        emit.passthrough(event)
        emit.keyup(evdev.ecodes.KEY_LEFTMETA)


class leftctrl(key):
    """when pressed solo go to the i3 container to the left (or right since i
    always run two vertical tab containers) otherwise emit KEY_LEFTCTRL.  this
    will be mapped to KEY_CAPSLOCK.

    """

    def __init__(self):
        super().__init__(passthrough=False)

    def keysolo(self):
        subprocess.run(["i3-msg", "focus parent; focus left"])

    def _keydown(self):
        emit.keydown(evdev.ecodes.KEY_LEFTCTRL)

    def _keyxcape(self, event):
        # this will be interpreted as CTRL+event.code
        emit.passthrough(event)

    def _keyup(self):
        emit.keyup(evdev.ecodes.KEY_LEFTCTRL)


class leftshift(key):
    # map to KEY_LEFTSHIFT in order to capture solo events.
    def __init__(self):
        super().__init__(passthrough=True)

    def keysolo(self):
        subprocess.run(["i3-msg", "focus left"])


class rightshift(key):
    # map to KEY_RIGHTSHIFT in order to capture solo events.
    def __init__(self):
        super().__init__(passthrough=True)

    def keysolo(self):
        subprocess.run(["i3-msg", "focus right"])


def winclass():
    # see: https://gist.github.com/budRich/892c0153c06a27ea7bc89d8f8dec99d2
    return subprocess.run(
        ["i3get", "-r c"], capture_output=True).stdout.lower().decode()

def ismediawin():
    win = winclass()
    if "google-chrome" in win:
        return True
    if "mpv" in win:
        return True
    return False


class volkey(key):
    """emit volume events when in a media window as defined in
    ismediawin(). currently the hold events are let through.

    """

    def __init__(self, ecode):
        super().__init__(passthrough=True)
        self._ecode = ecode

    def _keyup(self):
        return not ismediawin()

    def _keydown(self):
        if ismediawin():
            emit.keypress(self._ecode)
            return False
        return True
