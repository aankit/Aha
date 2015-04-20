#!/var/www/Aha/venv/bin/python

from camera import control
import logging

logging.basicConfig(filename=control.get_log_file(), level=logging.DEBUG)
refresh_state = control.record_refresh()
if refresh_state:
    #refresh happens...
    

    #this is a little bit of a safety net...still not certain my refresh code is super reliable
    # if new_file is None:
    #     new_filename = control.record_on()
    # elif new_file:
    #     new_filename = control.record_state()
    #maybe need to log this new file_name?

    #and now we can take an opportunity to do some strategic things
    from application import db
    from application.models import Video, Schedule, Marker
    from datetime import datetime
    import os

    def video_matches(db_model, date, day, start_time, end_time):
        matches = db.session.query(db_model) \
            .filter(db_model.day == day) \
            .filter(
                ((db_model.start_time <= start_time) & (db_model.end_time > start_time)) |
                ((db_model.start_time < end_time) & (db_model.end_time >= end_time)) |
                ((db_model.start_time > start_time) & (db_model.end_time < end_time))
            ).all()

        return matches

    #get the file that start 30 minutes ago and ended 15 minutes ago, its the second one
    file_index = 1
    filename = control.get_recording(file_index)
    filename_with_path = control.get_recording(file_index, full_path=True)
    if filename:
        #get the filename minus '.ts' since it is the date and time of the vid
        filename_date = filename[:-3]
        #get date, start and end time to see if we should save it.
        datetime_obj = datetime.strptime(filename_date, '%Y-%m-%d_%H-%M-%S')
        date = datetime.date(datetime_obj)
        day = date.weekday()
        start_time = datetime.time(datetime_obj)
        end_time_unix = os.path.getctime(filename_with_path)
        end_time = datetime.time(datetime.fromtimestamp(end_time_unix))
        print date, start_time, end_time

    # schedule_matches = video_matches(Schedule, date, start_time, end_time)
    # marker_matches = video_matches(Marker, date, start_time, end_time)

    # if schedule_matches or marker_matches:
    #     video_obj = Video(filename=filename, date=date, start_time=start_time, end_time=end_time)
    #     db.session.add(video_obj)
    #     for schedule_match in schedule_matches:
    #         schedule_match.videos.append(video_obj)
    #     for marker_match in marker_matches:
    #         marker_match.videos.append(video_obj)
    #     try:
    #         db.session.commit()
    #     except:
    #         db.session.rollback()
    #         print "couldn't write to the database"
    # else:
    #     control.remove_recording(file_index)