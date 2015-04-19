#!/var/www/Aha/venv/bin/python

from camera import control

refresh_state = control.recording_refresh()

if refresh_state is None:
    filename = control.record_on()
elif refresh_state:
    filename = control.refresh_state

print filename
