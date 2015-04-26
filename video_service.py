#!/var/www/Aha/venv/bin/python

from sh import ffmpeg
import os
import glob
import random
from datetime import datetime, timedelta
from application.models import Schedule, Marker
from application import media_dir

#let's get a list of files in each media subdirectory, if there is more than one, combine them
#using the vidlist.txt

today_string = datetime.strftime(datetime.now(), '%Y_%m_%d')
yest_string = datetime.strftime(datetime.now() - timedelta(days=1), '%Y_%m_%d')
print today_string
print yest_string

for date in [today_string, yest_string]:
    for model in [Schedule, Marker]:
        for result in model.query.all():
            print result
            try:
                investigation_id = str(result.investigation.id)
            except:
                investigation_id = "markers"  # markers don't initially have an investigation id

            media_path = media_dir + '/' + investigation_id + '/' + str(result.id) + '/' + date
            print media_path
            if os.path.isdir(media_path):
                vid_files = os.listdir(media_path)
                print vid_files
                if len(vid_files) > 1 and os.path.isfile(media_path + '/vidlist.txt'):
                    print "concating with ffmpeg"
                    ffmpeg('-f', 'concat', '-i', media_path + '/vidlist.txt',
                           '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc',
                           media_path + '/final.mp4/%s' % (datetime.strftime(datetime.now(), '%H-%M-%S')))
                    #save thumbnail
                    random_time = "%02d" % (random.randint(0, 30))
                    ffmpeg('-ss', '00:00:%s' % (random_time), "-i", media_path+'/final.mp4',
                           'frames:v', '1', media_path+'/thumbnail.jpg')
                    #get rid of old files
                    if datetime.now() > datetime.combine(date.today(), result.end_time) + timedelta(minutes=15):
                        os.remove(media_path+'/vidlist.txt')
                        for vid in glob.glob(media_path+'/*.ts'):
                            os.remove(vid)
