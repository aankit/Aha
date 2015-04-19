from camera import control

def refresh_recording():
    current_file = control.record_state()
    if current_file:
        control.record_off()
        control.record_on()
    else:
        print "nothing recording"

#TODO maybe save filename in database here