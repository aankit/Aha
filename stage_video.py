import aha

refresh_state = aha.refresh_camera()
if refresh_state:
    last_recording = aha.get_last_recorded()
    aha.stage_file(last_recording)
