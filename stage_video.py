import aha
from glob import glob
refresh_state = aha.refresh_camera()
if refresh_state:
    last_recording = aha.get_last_recorded()
    aha.stage_file(last_recording)
else if aha.get_all_recorded():
    for recording in aha.get_all_recorded():
        aha.stage_file(recording)
