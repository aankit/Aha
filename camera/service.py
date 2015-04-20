#!/var/www/Aha/venv/bin/python

import control
import logging

logging.basicConfig(filename=control.get_log_file(), level=logging.DEBUG)

if control.service_state():
    #refresh happens...
    refresh_state = control.record_refresh()

    #this is a little bit of a safety net...still not certain my refresh code is super reliable
    if refresh_state is None:
        new_filename = control.record_on()
    elif refresh_state:
        new_filename = control.record_state()
    #maybe need to log this new file_name?

    #and now we can take an opportunity to do some strategic things
    from application import db
    from application.models import Video, Schedule, Marker
    from datetime import datetime, timedelta

    def keepVideo(db_model, date, start_time, end_time):
        day = date.weekday()

        matches = db.session.query(db_model) \
            .filter(db_model.day == day) \
            .filter(
                ((db_model.start_time <= start_time) & (db_model.end_time > start_time)) |
                ((db_model.start_time < end_time) & (db_model.end_time >= end_time))
            ).first()

        if matches:
            return True
        else:
            return False

    #get the file that start 30 minutes ago and ended 15 minutes ago, its the second one
    file_index = 1
    filename = control.get_recording(file_index)
    #get the filename minus '.ts' since it is the date and time of the vid
    filename_date = filename[:-3]
    #get date, start and end time to see if we should save it.
    datetime_obj = datetime.strptime(filename_date, '%Y-%m-%d_%H-%M-%S')
    date = datetime.date(datetime_obj)
    start_time = datetime.time(datetime_obj)
    end_time = datetime.time(datetime_obj+timedelta(minutes=15))  # for comparison purposes, won't be saved
    print date, start_time, end_time

    if keepVideo(Schedule, date, start_time, end_time) or keepVideo(Marker, date, start_time, end_time):
        video_obj = Video(filename=filename, date=date, start_time=start_time)
        db.session.add(video_obj)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            print "couldn't write to the database"
    else:
        control.remove_recording(file_index)
