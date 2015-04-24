from sh import ffmpeg
import os
from datetime import datetime
from application.models import Schedule, Marker
from application import app

#let's get a list of files in each media subdirectory, if there is more than one, combine them
#using the vidlist.txt

string_date = datetime.strftime(datetime.now(), '%Y_%m_%d')

for model in [Schedule, Marker]:
    for result in model.query.all():
        try:
            investigation_id = str(model.investigation.id)
        except:
            investigation_id = "markers"  # markers don't initially have an investigation id

        media_path = app.config['MEDIA_DIR'] + '/' + investigation_id + '/' + str(result.id) + '/' + string_date
        vid_files = os.listdir(media_path)
        if len(vid_files) > 1:
            ffmpeg('-f', 'concat', '-i', 'vidlist.txt')
