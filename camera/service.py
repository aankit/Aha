from camera import control

refresh_state = control.recording_refresh()

if refresh_state is None:
    filename = contorl.record_on()
elif refresh_state:
    filename = control.refresh_state

print filename
