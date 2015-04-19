#!/var/www/Aha/venv/bin/python

import control

if control.service_state():
    #refresh happens...
    old_filename = control.record_state()
    refresh_state = control.record_refresh()

    #this is a little bit of a safety net...still not certain my refresh code is super reliable
    if refresh_state is None:
        filename = control.record_on()
    elif refresh_state:
        filename = control.record_state()

    from application import db
    from application.models import Video, Schedule, Marker
    from datetime import datetime
    #and now we can take an opportunity to do some strategic things
    #1) save the old file
    #2) ask DB for marker start times and marker end times that happened during last video
    #3) ask DB for schedule start time and schedule end times that happened during last video

    filename_date = control.get_recording()[:-3]
    datetimestamp = datetime.strptime(filename_date, '%Y-%m-%d_%H-%M-%S')
    date = datetime.date(datetimestamp)
    start_time = datetime.time(datetimestamp)

    video_obj = Video(filename=old_filename, date=date, start_time=start_time)

    def check_cuts(db_model, video_obj):
        #does the video start inside and end outside a schedule or marker?
        si_eo = db.session.query(db_model). \
            filter(db_model.start_time >= video_obj.start_time) & (db_model.end_time >= video_obj.end_time)
        #does the video start outside end inside a schedule or marker?
        so_ei = db.session.query(db_model). \
            filter(db_model.start_time <= video_obj.start_time) & (db_model.end_time <= video_obj.end_time)
        #does the video start inside and end inside a schedule or marker?
        si_ei = db.session.query(db_model). \
            filter(db_model.start_time >= video_obj.start_time) & (db_model.end_time <= video_obj.end_time)
        #does the video start outside and end outside a scheduler or marker
        so_eo = db.session.query(db_model). \
            filter(db_model.start_time <= video_obj.start_time) & (db_model.end_time >= video_obj.end_time)

