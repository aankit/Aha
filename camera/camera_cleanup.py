import control, settings
from datetime import datetime
import os
from application import media_dir

for filepath in control.get_all_recordings():
    filename = filepath[len(settings.ARCHIVE_RECORDING_PATH):-3]
    print filename
