#!/var/www/Aha/venv/bin/python

from sh import ffmpeg
import os
import glob
import random
from datetime import datetime, timedelta
from application.models import Schedule, Marker
from application import media_dir


def process_media(media_path):
    if os.path.isdir(media_path):
        print media_path
        vid_files = glob.glob(media_path+'/*.ts')
        final_filename = media_path + '/final.mp4'
        thumbnail = media_path + '/thumbnail.jpg'
        if len(vid_files) > 1 and os.path.isfile(media_path + '/vidlist.txt'):
            concatenate(final_filename, media_path)
            thumbnail(final_filename, thumbnail)
        elif len(vid_files) == 1:
            transcode(vid_files[0], final_filename, media_path)


def thumbnail(final_filename, thumbnail):
    #save thumbnail
    if os.path.isfile(thumbnail):
        os.remove(thumbnail)
    random_time = str(random.randint(0, 30)).zfill(2)
    ffmpeg('-ss', '00:00:%s' % (random_time), "-i", final_filename,
           '-frames:v', '1', thumbnail)


def concatenate(final_filename, media_path):
    if os.path.isfile(final_filename):
        os.remove(final_filename)
    ffmpeg('-f', 'concat', '-i', media_path + '/vidlist.txt',
           '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', final_filename)
    #get rid of old files
    right_now = datetime.time(datetime.now())
    fifteen_after = datetime.time(datetime.combine(date.today(), result.end_time) + timedelta(minutes=15))
    if right_now > fifteen_after or right_now < result.end_time:
        os.remove(media_path+'/vidlist.txt')
        for vid in glob.glob(media_path+'/*.ts'):
            os.remove(vid)


def transcode(ts_filename, final_filename, media_path):
    if os.path.isfile(final_filename):
        os.remove(final_filename)
    ffmpeg('-i', ts_filename, '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', final_filename)
    os.remove(ts_filename)


today_string = datetime.strftime(datetime.now(), '%Y_%m_%d')
yest_string = datetime.strftime(datetime.now() - timedelta(days=1), '%Y_%m_%d')

for date in [today_string, yest_string]:
    for model in [Schedule, Marker]:
        for result in model.query.all():
            media_path = media_dir
            try:
                media_path += "/".join([str(result.investigation.id), str(result.id), date])
            except:
                media_path += "/".join(["markers", str(result.id)])
            process_media(media_path)
