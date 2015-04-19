#!/usr/bin/env python

from camera import control

refresh_state = control.record_refresh()

if refresh_state is None:
    filename = control.record_on()
elif refresh_state:
    filename = control.record_state()

print filename
