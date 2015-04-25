#!/var/www/Aha/venv/bin/python

from sh import ffmpeg
import os
from datetime import datetime
from application.models import Schedule, Marker
from application import media_dir

#let's get a list of files in each media subdirectory, if there is more than one, combine them
#using the vidlist.txt

string_date = datetime.strftime(datetime.now(), '%Y_%m_%d')
print string_date
for model in [Schedule, Marker]:
    for result in model.query.all():
        print result
        try:
            investigation_id = str(model.investigation.id)
        except:
            investigation_id = "markers"  # markers don't initially have an investigation id

        media_path = media_dir + '/' + investigation_id + '/' + str(result.id) + '/' + string_date
        print media_path
        if os.path.isdir(media_path):
            vid_files = os.listdir(media_path)
            print vid_files
            if len(vid_files) > 1 and os.path.isfile(media_path + '/' + 'vidlist.txt'):
                ffmpeg('-f', 'concat', '-i', 'vidlist.txt')
