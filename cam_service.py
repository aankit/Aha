#!/var/www/Aha/venv/bin/python

from camera import control
import logging

logging.basicConfig(filename=control.get_log_file(), level=logging.DEBUG)
#refresh happens...
refresh_state = control.record_refresh()

#if we had a refresh let's go ahead with some file evaluation
if refresh_state:
    from application import app, db
    from application.models import Video, Schedule, Marker
    from datetime import datetime, date
    import os
    from sh import ffmpeg

    #check database for matches
    def video_matches(db_model, vid_starttime_obj, vid_endtime_obj):
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
            start_time_diff = vid_starttime_obj - datetime.combine(vid_date, match.start_time)
            end_time_diff = vid_endtime_obj - datetime.combine(vid_date, match.end_time)
            #get the clock timestamps of the start and end time that we need from this particular video
            cut_start_time = match.start_time if start_time_diff.seconds > 15*60 else vid_start_time
            cut_end_time = vid_end_time if end_time_diff.seconds > 15*60 else match.end_time
            #check to see if media path exists or make it
            try:
                investigation_id = str(match.investigation.id)
            except
                investigation_id = "markers"
            media_path = app.config['MEDIA_URL'] + '/' + investigation_id + '/' + str(match.id) + '/' + string_date)
            if not os.path.isdir(media_path):
                sh.mkdir(media_path)


                


        return matches


    #get the file that start 30 minutes ago and ended 15 minutes ago, its the second one
    file_index = 1
    filename = control.get_recording(file_index)
    filename_with_path = control.get_recording(file_index, full_path=True)
    if filename:
        #get the filename minus '.ts' since it is the date and time of the vid
        filename_date = filename[:-3]
        #get date, start and end time to see if we should save it.
        starttime_obj = datetime.strptime(filename_date, '%Y-%m-%d_%H-%M-%S')
        endtime_obj = datetime.fromtimestamp(os.path.getctime(filename_with_path))

        schedule_matches = video_matches(Schedule, starttime_obj, endtime_obj)
        marker_matches = video_matches(Marker, date, day, start_time, end_time)

