#!/var/www/Aha/venv/bin/python

import camera.settings
import camera.control
import application.settings
from application import db
from application.models import Schedule, Marker, Video
from sh import mv, ffmpeg, ffprobe, mkdir, touch
from datetime import datetime, timedelta
import os
import glob
import random
import logging

logging.basicConfig(filename='aha.log', level=logging.INFO)


def refresh_camera():
    refresh_state = camera.control.record_refresh()
    get_last_recorded
    return refresh_state


def refresh_sleep():
    return camera.settings.VIDEO_CHUNK_LENGTH

#manage staging directory


def stage_file(filename):
    logging.info("moving the %s" % (filename))
    mv(filename, application.settings.MEDIA_DIR + '/staging')


def sort_videos(filename):
    starttime_obj, endtime_obj = get_file_timestamps(filename)
    return starttime_obj


def get_staged_files():
    staged_files = glob.glob(application.settings.STAGING_DIR+"/*.ts")
    sorted_staged_files = sorted(staged_files, key=sort_videos)
    return sorted_staged_files


def check_purge_state(filename):
    vid_starttime_obj, vid_endtime_obj = get_file_timestamps(filename)
    time_diff = datetime.now() - vid_endtime_obj
    if time_diff.seconds >= 16*60:
        return True


#manage recording directory


def get_last_recorded():
    return camera.control.get_recording(1, full_path=True)


def get_all_recorded():
    return camera.control.get_all_recordings()


def get_db_matches(filename):
    matches = []
    for db_model in [Schedule, Marker]:
        vid_starttime_obj, vid_endtime_obj = get_file_timestamps(filename)
        if vid_endtime_obj.day > vid_starttime_obj.day:
            continue
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
        # print "successfully made %s" % (media_path)
        commit_to_db(media_path, match)
        # print "path exists: %s" % (media_path)
    return media_path


def get_media_paths():
    media_paths = []
    for db_model in [Schedule, Marker]:
        #collect media paths to return
        for result in db_model.query.all():
            if result.videos:
                end_time = datetime.combine(datetime.today(), result.end_time)
                start_time = datetime.combine(datetime.today(), result.start_time)
                duration = end_time - start_time
                for video in result.videos:
                    if glob.glob(application.settings.APPLICATION_DIR+video.media_path+'/*.ts'):
                        media_paths.append((application.settings.APPLICATION_DIR+video.media_path, duration.seconds))
    return media_paths


def get_sorted_filenames(media_path):
    filenames = glob.glob(media_path+'/*.ts')
    sorted_filenames = sorted(filenames, key=sort_videos)
    return sorted_filenames


def check_duration(media_path):
    sorted_filenames = get_sorted_filenames(media_path)
    duration = 0
    for filename in sorted_filenames:
        duration += check_file_duration(filename)
    logging.info("the cumulative duration of the ts files: %d" % (duration))
    return duration


def check_file_duration(filename):
    try:
        ffout = ffprobe('-i', filename, '-show_format', '-v', 'quiet')
        ffout = ffout.strip()
        ffout_list = ffout.split()
        duration = [output.split("=")[1] for output in ffout_list if "duration" in output][0]
    except:
        duration = 0.0
    return float(duration)


def check_consecutive(media_path):
    sorted_filenames = get_sorted_filenames(media_path)
    gaps = 0
    logging.info("Media Path: %s" % (media_path))
    for index in range(1, len(sorted_filenames)):
        first_starttime_obj, first_endtime_obj = get_file_timestamps(sorted_filenames[index-1])
        second_starttime_obj, second_endtime_obj = get_file_timestamps(sorted_filenames[index])
        time_diff = second_starttime_obj - first_endtime_obj
        logging.info("%d: %d between %s & %s" % (index, time_diff.seconds, sorted_filenames[index], sorted_filenames[index-1]))
        gaps += time_diff.seconds
    logging.info("Total Gap: %d for %d" % (gaps, len(sorted_filenames)))
    return gaps, len(sorted_filenames)


def clean_build_media(media_path):
    ts_files = glob.glob(media_path+'/*.ts')
    txt_files = glob.glob(media_path+'/*.txt')
    for ts_file in ts_files:
        os.remove(ts_file)
    for txt_file in txt_files:
        os.remove(txt_file)
    touch(media_path+'/complete')

#cut recorded/staged file into media path


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


def cut_file(media_path, filename, match):
    media_filename = media_path + '/' + remove_path(filename)
    ffmpeg_start, ffmpeg_duration = get_relative_cut(filename, match)
    #now cut the vid and save it in the media directory, run it as a background to keep this moving
    ffmpeg('-ss', ffmpeg_start,
           '-i', filename,
           '-to', ffmpeg_duration,
           '-c', 'copy',
           '-avoid_negative_ts', '1',
           media_filename)
    concat_filename = media_path+'/vidlist.txt'
    append_concat_file(concat_filename, media_filename)

#manage media directories


def append_concat_file(concat_filename, filename):
    #now we need to create or append to the directory's concat text file for ffmpeg later on
    if not os.path.isfile(concat_filename):
        touch(concat_filename)
    with open(concat_filename, 'a') as vidlist:
        vidlist.write('file ' + "'" + filename + "'")
        vidlist.write('\n')


def build_ready(media_path):
    concat_file = media_path+'/vidlist.txt'
    if concat_file:
        return True


def new_file_exists(media_path):
    video = media_path+'/video.mp4'
    if os.path.isfile(video):
        video_duration = check_file_duration(video)
        files_duration = check_duration(media_path)
        if files_duration > video_duration+15:  # the +15 (seconds) is a margin of error, might be smaller
            return True
        else:
            return False
    else:
        return True


def sort_concat_file(media_path):
    ''' this a bit of redundancy, its a check '''
    concat_file = media_path+'/vidlist.txt'
    with open(concat_file, 'r') as vidlist:
        read_data = vidlist.read()
    read_data = read_data.strip()
    concat_list = read_data.split('\n')
    filenames = [f.split(" ")[1][1:-1] for f in concat_list]
    sorted_filenames = sorted(filenames, key=sort_videos)
    sorted_concat_filename = media_path + '/sorted_vidlist.txt'
    if os.path.isfile(sorted_concat_filename):
        os.remove(sorted_concat_filename)
    for filename in sorted_filenames:
        append_concat_file(sorted_concat_filename, filename)


def transcode(media_path, filename):
    output_filename = media_path + "/video.mp4"
    ffmpeg('-i', media_path + '/' + filename,
            '-c:v', 'copy', '-c:a', 'copy', '-bsf:a', 'aac_adtstoasc', output_filename)
    os.remove(media_path + '/' + filename)


def concatenate(media_path):
    filename = media_path + "/video.mp4"
    if os.path.isfile(filename):
        os.remove(filename)
    ffmpeg('-f', 'concat', '-i', media_path + '/sorted_vidlist.txt',
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
            # print "video added to DB %s" % (media_path)
        except:
            db.session.rollback()
            # print "committing to DB didn't work."
    # else:
    #     print "media path already in db"


#utility functions

def remove_path(fname):
    if len(fname) > 22:
        return fname[-22:]  # this works only because of the file date structure
    else:
        return fname


def get_file_timestamps(filename):
    #get date, start and end time to see if we should save it.
    starttime_obj = datetime.strptime(remove_path(filename)[:-3], '%Y-%m-%d_%H-%M-%S')
    duration = check_file_duration(filename)
    endtime_obj = starttime_obj + timedelta(seconds=duration)
    return starttime_obj, endtime_obj
