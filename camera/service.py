from camera.control import *

refresh_state = recording_refresh()

if refresh_state is None:
    filename = record_on()
elif refresh_state:
    filename = refresh_state

print filename
