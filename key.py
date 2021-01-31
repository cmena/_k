class key:
    def __init__(self, passthrough):
        self._down = False
        self._xcaped = False
        self._passthrough = passthrough

    # key events: with the exception of keyxcape, these correspond to evdev key
    # events. see `key handlers` below.

    def keydown(self):
        self._down = True
        v = self._keydown()
        # override self._passthrough
        if v is not None:
            return v
        return self._passthrough

    def keyheld(self):
        assert(self._down)
        v = self._keyheld()
        # override self._passthrough
        if v is not None:
            return v
        return self._passthrough

    def keyup(self):
        self._down = False
        v = self._keyup()
        # override self._passthrough
        if v is not None:
            return v
        return self._passthrough

    def keyxcape(self, event):
        """a keydown event where self was used as a modifier ie, xcaped."""
        self._xcaped = True
        v = self._keyxcape(event)
        # override self._passthrough
        if v is not None:
            return v
        return self._passthrough

    # key handlers: implement to add functionality to corresponding events. if
    # a value is returned, bool(value) will be used to override
    # self._passthrough.  see `key events` above.

    def _keydown(self):
        pass

    def _keyheld(self):
        pass

    def _keyup(self):
        pass

    def _keyxcape(self, event):
        pass

    # virtual events

    def keyreset(self, xcape=True):
        if xcape:
            self._xcaped = False

    def keysolo(self):
        pass

    # --

    def isxcaped(self):
        return self._xcaped
