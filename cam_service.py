#!/var/www/Aha/venv/bin/python

from camera import control
import logging

logging.basicConfig(filename=control.get_log_file(), level=logging.DEBUG)
#refresh happens...
refresh_state = control.record_refresh()

#if we had a refresh let's go ahead with some file evaluation
if refresh_state:
    from application import app, db
    from application.models import Schedule, Marker
    from datetime import datetime, date
    import os
    from sh import ffmpeg, mkdir, touch

    #check database for matches
    def video_matches(db_model, filename, filename_with_path, vid_starttime_obj, vid_endtime_obj):
        #get the relevant information for the video
        vid_date = datetime.date(starttime_obj)
        vid_day = date.weekday()
        vid_start_time = datetime.time(vid_starttime_obj)
        vid_end_time = datetime.time(vid_endtime_obj)
        #find the matches in the db
        matches = db.session.query(db_model) \
            .filter(db_model.active == True) \
            .filter(db_model.day == vid_day) \
            .filter(
                ((db_model.start_time <= vid_start_time) & (db_model.end_time > vid_start_time)) |
                ((db_model.start_time < vid_end_time) & (db_model.end_time >= vid_end_time)) |
                ((db_model.start_time >= vid_start_time) & (db_model.end_time <= vid_end_time))
            ).all()

        for match in matches:
            vid_string_date = datetime.strftime(vid_date, '%Y_%m_%d')
            #does the vid start or end come after match start or end respectively?
            match_starttime_obj = datetime.combine(vid_date, match.start_time)
            match_endtime_obj = datetime.combine(vid_date, match.end_time)
            start_time_diff = match_starttime_obj - vid_starttime_obj
            end_time_diff = match_endtime_obj - vid_endtime_obj
            #get the clock timestamps of the start and end time that we need from this particular video
            cut_start_time = match_starttime_obj if start_time_diff.seconds < 15*60 else vid_starttime_obj
            cut_end_time = vid_endtime_obj if end_time_diff.seconds < 15*60 else match_endtime_obj
            #get the initial video time to cut from to use in ffmpeg -ss function
            ffmpeg_start = str(cut_start_time - vid_starttime_obj)
            #get the video duration, cut_end - cut start to use in ffmpeg -ss function
            ffmpeg_duration = str(cut_end_time - cut_start_time)
            #check to see if media path exists or make it
            try:
                investigation_id = str(match.investigation.id)
            except:
                investigation_id = "markers"  # markers don't initially have an investigation id
            #since these are just snippets of files, I'm saving them to a place where they can be combined later
            media_path = app.config['MEDIA_DIR'] + '/' + investigation_id + '/' + str(match.id) + '/' + vid_string_date
            if not os.path.isdir(media_path):
                mkdir(media_path)
            #now cut the vid and save it in the media directory, run it as a background to keep this moving
            cut_process = ffmpeg('-ss', ffmpeg_start,
                                 '-i', filename_with_path,
                                 '-to', ffmpeg_duration,
                                 '-c', 'copy',
                                 '-avoid_negative_ts', '1',
                                 media_path+'/'+filename,
                                 _bg=True)
            #now we need to create or append to the directory's concat text file for ffmpeg later on
            if not os.path.isfile(media_path+'/'+'vidlist.txt'):
                touch(media_path+'/'+'vidlist.txt')
            with open(media_path+'/'+'vidlist.txt', 'a') as vidlist:
                vidlist.write(filename)
        return 0


    #get the file that start 30 minutes ago and ended 15 minutes ago, its the second one
    file_index = 1
    filename, filename_with_path = control.get_recording(file_index, full_path=True)
    if filename:
        #get the filename minus '.ts' since it is the date and time of the vid
        filename_date = filename[:-3]
        #get date, start and end time to see if we should save it.
        starttime_obj = datetime.strptime(filename_date, '%Y-%m-%d_%H-%M-%S')
        endtime_obj = datetime.fromtimestamp(os.path.getctime(filename_with_path))

        schedule_matches = video_matches(Schedule, filename, filename_with_path, starttime_obj, endtime_obj)
        marker_matches = video_matches(Marker, filename, filename_with_path, starttime_obj, endtime_obj)
