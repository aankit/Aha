#!/var/www/Aha/venv/bin/python

from sh import ffmpeg
import os
import glob
import random
from datetime import datetime, timedelta, date
from application.models import Schedule, Marker, Video
from application import media_dir, db


def process_media(media_path):
    if os.path.isdir(media_path):
        vid_files = glob.glob(media_path+'/*.ts')
        final_filename = media_path + '/final.mp4'
        thumbnail = media_path + '/thumbnail.jpg'
        if len(vid_files) > 1 and os.path.isfile(media_path + '/vidlist.txt'):
            # print media_path
            concatenate(final_filename, media_path)
        elif len(vid_files) == 1:
            # print media_path
            transcode(vid_files[0], final_filename, media_path)
        make_thumbnail(final_filename, thumbnail)
        commit_to_db()


def concatenate(final_filename, media_path):
    if os.path.isfile(final_filename):
        os.remove(final_filename)
    ffmpeg('-f', 'concat', '-i', media_path + '/vidlist.txt',
           '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', final_filename)


def transcode(ts_filename, final_filename, media_path):
    if os.path.isfile(final_filename):
        os.remove(final_filename)
    ffmpeg('-i', ts_filename, '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', final_filename)


def make_thumbnail(final_filename, thumbnail):
    #save thumbnail
    if not os.path.isfile(thumbnail):
        random_time = str(random.randint(0, 30)).zfill(2)
        ffmpeg('-ss', '00:00:%s' % (random_time), "-i", final_filename,
               '-frames:v', '1', thumbnail)


def commit_to_db(media_path):
    #oh hello, we are going to add that this video has bee made!
    private_path = '/var/www/Aha'
    public_media_path = media_path[len(private_path):]
    video_obj = Video.query.filter_by(media_path=public_media_path).first()
    if not video_obj:
        new_video_obj = Video(media_path=public_media_path, date=datetime.today())
        db.session.add(new_video_obj)
        result.videos.append(new_video_obj)
        try:
            db.session.commit()
            print "video added to DB"
        except:
            db.session.rollback()
            print "committing to DB didn't work."


def complete_video_build(media_path, result):
    ts_files = [f for f in glob.glob(media_path+'/*.ts')]
    sorted_ts_files = sorted(ts_files, key=os.path.getctime, reverse=True)
    latest_datetime = datetime.strptime(sorted_ts_files[0][len(media_path)+1:-3], '%Y-%m-%d_%H-%M-%S')
    fifteen_after = datetime.combine(date.today(), result.end_time) + timedelta(minutes=15)
    fifteen_before = datetime.combine(date.today(), result.start_time) + timedelta(minutes=15)
    if latest_datetime < fifteen_before or latest_datetime > fifteen_after:
        try:
            os.remove(media_path+'/vidlist.txt')
            for vid in glob.glob(media_path+'/*.ts'):
                os.remove(vid)
                print "removed: %s" % (vid)
        except:
            print "files couldn't be removed, we'll have to try this again."


today_string = datetime.strftime(datetime.now(), '%Y_%m_%d')
yest_string = datetime.strftime(datetime.now() - timedelta(days=1), '%Y_%m_%d')

for date_string in [today_string, yest_string]:
    for model in [Schedule, Marker]:
        for result in model.query.all():
            try:
                media_path = "/".join([media_dir, str(result.investigation.id), str(result.id), date_string])
            except:
                media_path = "/".join([media_dir, "markers", str(result.id)])
            process_state = process_media(media_path)
            if process_state > 2:
                complete_video_build(media_path, result)
