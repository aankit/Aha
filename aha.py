#!/var/www/Aha/venv/bin/python

import camera.settings
import camera.control
import application.settings
from application import db
from application.models import Schedule, Marker, Video
from sh import mv, ffmpeg, mkdir, touch
from datetime import datetime, timedelta
import os
import glob
import random


def refresh_camera():
    refresh_state = camera.control.record_refresh()
    get_last_recorded
    return refresh_state


#manage staging directory

def stage_file(filename):
    mv(filename, application.settings.MEDIA_DIR + '/staging')


def sort_videos(filename):
    starttime_obj, endtime_obj = get_file_timestamps(filename)
    return starttime_obj


def get_staged_files():
    staged_files = glob.glob(application.settings.STAGING_DIR+"/*.ts")
    sorted_staged_files = sorted(staged_files, key=sort_videos, reverse=True)
    return sorted_staged_files


def check_purge_state(filename):
    vid_starttime_obj, vid_endtime_obj = get_file_timestamps(filename)
    time_diff = datetime.now() - vid_endtime_obj
    if time_diff.seconds >= 15*60:
        return True


#manage recording directory


def get_last_recorded():
    return camera.control.get_recording(1, full_path=True)


def get_all_recorded():
    return camera.control.get_all_recordings()


def get_file_matches(filename):
    matches = []
    for db_model in [Schedule, Marker]:
        vid_starttime_obj, vid_endtime_obj = get_file_timestamps(filename)
        vid_date = datetime.date(vid_starttime_obj)
        vid_day = vid_date.weekday()
        vid_start_time = datetime.time(vid_starttime_obj)
        vid_end_time = datetime.time(vid_endtime_obj)
        #find the matches in the db
        #first if its a schedule, we need to look for actives, might as well get day in there as well
        if db_model == Schedule:
            active_matches = db.session.query(db_model).filter_by(active=True).filter_by(day=vid_day)
        else:
            #in the case of markers, they are all active and there is only one per date
            active_matches = db.session.query(db_model).filter_by(date=vid_date)
        #now get matches based on time
        model_matches = active_matches \
            .filter(
                ((db_model.start_time <= vid_start_time) & (db_model.end_time > vid_start_time)) |
                ((db_model.start_time < vid_end_time) & (db_model.end_time >= vid_end_time)) |
                ((db_model.start_time >= vid_start_time) & (db_model.end_time <= vid_end_time)) |
                ((db_model.start_time < vid_start_time) & (db_model.end_time > vid_end_time))
            ).all()
        matches += model_matches
    return matches


def get_media_paths():
    media_paths = []
    for db_model in [Schedule, Marker]:
        model_media_paths = [video.media_path for result in db_model.query.all() if result.videos for video in result.videos]
        media_paths += model_media_paths
    return media_paths


def get_media_path(filename, match):
    vid_starttime_obj, vid_endtime_obj = get_file_timestamps(filename)
    vid_date = datetime.date(vid_starttime_obj)
    vid_string_date = datetime.strftime(vid_date, '%Y_%m_%d')
    media_dir = application.settings.MEDIA_DIR
    #check to see if media path exists or make it
    try:
        media_path = "/".join([media_dir, str(match.investigation.id), str(match.id), vid_string_date])
    except:
        media_path = "/".join([media_dir, "markers", str(match.id)])
    if not os.path.isdir(media_path):
        mkdir('-p', media_path)
        print "successfully made %s" % (media_path)
        commit_to_db(media_path, match)
    else:
        print "path exists: %s" % (media_path)
    return media_path


def check_media_path(media_path):
    filenames = glob.glob(media_path+'/*.ts')
    sorted_filenames = sorted(filenames, key=sort_videos, reverse=True)
    first_file = sorted_filenames[0]
    last_file = sorted_filenames[-1]
    print first_file
    print last_file


def get_relative_cut(filename, match):
    vid_starttime_obj, vid_endtime_obj = get_file_timestamps(filename)
    vid_date = datetime.date(vid_starttime_obj)
    #does the vid start or end come after match start or end respectively?
    match_starttime_obj = datetime.combine(vid_date, match.start_time)
    match_endtime_obj = datetime.combine(vid_date, match.end_time)
    start_time_diff = match_starttime_obj - vid_starttime_obj
    end_time_diff = match_endtime_obj - vid_endtime_obj

    #get the clock timestamps of the start and end time that we need from this particular video
    cut_start_time = match_starttime_obj if start_time_diff.seconds < 15*60 else vid_starttime_obj
    cut_end_time = vid_endtime_obj if end_time_diff.seconds < 15*60 else match_endtime_obj
    if cut_end_time < cut_start_time:
        return False  # this is the midnight scenario

    #get the initial video time to cut from to use in ffmpeg -ss function
    start = str(cut_start_time - vid_starttime_obj)
    #get the video duration, cut_end - cut start to use in ffmpeg -ss function
    duration = str(cut_end_time - cut_start_time)
    return start, duration


#cut recorded/staged file into media path

def cut_file(filename, match):
    media_path = get_media_path(filename, match)
    media_filename = media_path + '/' + remove_path(filename)
    ffmpeg_start, ffmpeg_duration = get_relative_cut(filename, match)
    #now cut the vid and save it in the media directory, run it as a background to keep this moving
    ffmpeg('-ss', ffmpeg_start,
           '-i', filename,
           '-to', ffmpeg_duration,
           '-c', 'copy',
           '-avoid_negative_ts', '1',
           media_filename)
    #now we need to create or append to the directory's concat text file for ffmpeg later on
    if not os.path.isfile(media_path+'/'+'vidlist.txt'):
        touch(media_path+'/'+'vidlist.txt')
    with open(media_path+'/'+'vidlist.txt', 'a') as vidlist:
        vidlist.write('file ' + "'" + media_path + '/' + filename + "'")
        vidlist.write('\n')


#manage media directories

def concatenate(media_path):
    filename = media_path + "/video.mp4"
    if os.path.isfile(filename):
        os.remove(filename)
    ffmpeg('-f', 'concat', '-i', media_path + '/vidlist.txt',
           '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', filename)


def make_thumbnail(media_path):
    thumbnail = media_path + '/thumbnail.jpg'
    video = media_path + '/video.mp4'
    #save thumbnail
    if not os.path.isfile(thumbnail):
        random_time = str(random.randint(0, 30)).zfill(2)
        ffmpeg('-ss', '00:00:%s' % (random_time), "-i", video,
               '-frames:v', '1', thumbnail)


def commit_to_db(media_path, match):
    #oh hello, we are going to add that this video has bee made!
    private_path = '/var/www/Aha'
    public_media_path = media_path[len(private_path):]
    video_obj = Video.query.filter_by(media_path=public_media_path).first()
    if not video_obj:
        new_video_obj = Video(media_path=public_media_path, date=datetime.today())
        db.session.add(new_video_obj)
        match.videos.append(new_video_obj)
        try:
            db.session.commit()
            print "video added to DB %s" % (media_path)
        except:
            db.session.rollback()
            print "committing to DB didn't work."
    else:
        print "media path already in db"

#video utility functions


def remove_path(fname):
    return fname[-22:]  # this works only because of the file date structure


def get_file_timestamps(filename):
    #get date, start and end time to see if we should save it.
    starttime_obj = datetime.strptime(remove_path(filename)[:-3], '%Y-%m-%d_%H-%M-%S')
    endtime_obj = starttime_obj + timedelta(minutes=camera.settings.VIDEO_CHUNK_LENGTH)
    return starttime_obj, endtime_obj
