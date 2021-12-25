## _k: a keyboard re-mapper for linux using evdev

### Install

1. add user to input group
2. add the following udev rule:
   ``` KERNEL=="uinput", GROUP="input", MODE="0660" ```
3. load the ```uinput``` kernel module at boot. in debian add it to /etc/modules.

### Run
_k profile.py

profiles are python files that are eval'ed in the current environment. there are example profiles under _k/etc.
