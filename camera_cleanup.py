#!/var/www/Aha/venv/bin/python

from camera import control, settings
from datetime import datetime
import os
from application import media_dir

for filepath in control.get_all_recordings():
    filename = filepath[len(settings.ARCHIVE_RECORDING_PATH)+1:-3]
    starttime_obj = datetime.strptime(filename, '%Y-%m-%d_%H-%M-%S')
    time_diff = datetime.now() - starttime_obj
    if time_diff.seconds > 30*60:
        os.remove(filepath)
        print "removed: %s" % (filepath)
