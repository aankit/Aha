from application.models import *
from application.schedulerConfig import scheduler
from application import picam
from application import db
from datetime import datetime
import time


def cam_record(schedule_id, start_time=None):
    '''
    Turns the picam service on if not on,
    starts recording, ending existing recording,
    and saves the new video in DB.

    Returns the video_id, if any.
    '''
    # create start timestamp if none provided
    if start_time is None:
        t = datetime.now()
        start_time = datetime(t.year, t.month, t.day, t.hour, t.minute)
    #check state of camera
    picam_pid = picam.service_state()
    recording_filename = picam.record_state()
    #get to ready state based on state
    if not picam_pid:
        picam.service_on()
        time.sleep(2)
    if recording_filename:
        cam_off()
        picam.service_on()
        time.sleep(2)
    #start recording
    try:
        recording_filename = picam.record_on()
        video_obj = Video(filename=recording_filename, start_time=start_time, schedule_id=schedule_id)
        db.session.add(video_obj)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return error
    video_id = video_obj.id
    return video_id


def cam_off():
    '''
    Turns the current picam recording off if recording,
    turns the picam service_off if on
    '''
    picam_pid = picam.service_state()
    recording_filename = picam.record_state()
    if recording_filename:
        picam.record_off()
    if picam_pid:
        picam.service_off()
    return 0


def process_video(event):
    '''
    Runs as APScheduler JOB_EXECUTION_EVENT | JOB_ERROR_EVENT
    for use after the cam_off event is called by application scheduler.
    '''
    if event.exception:
        app.logger.info('the job failed :(')
    else:
        app.logger.info('The job worked :)')
    # found_markers = {}
    # video = db.session.query(Video).filter_by(id=event.retval).first()
    # m = db.session.query(Marker).filter_by(video_id=video.id).all()
    # found_markers[video.id] = []
    # for fm in m:
    #     found_markers[video.id].append(fm)


def add_jobs(form, day, section_id):
    #store the times
    schedule_obj = Schedule(day=day,
      start_time=form.start_time.data,
      end_time=form.end_time.data,
      section_id=section_id)
    db.session.add(schedule_obj)
    try:
        db.session.commit()
    except Exception as error:
        return "couldn't add schedule obj", error
    #create job ids
    start_job_id = "section_%s-schedule_%d-start" % (section_id, schedule_obj.id)
    end_job_id = "section_%s-schedule_%d-end" % (section_id, schedule_obj.id)
    #create cron jobs
    try:
        scheduler.add_job(cam_record, "cron",
            kwargs={"schedule_id": schedule_obj.id},
            id=start_job_id,
            day_of_week=day,
            hour=form.start_time.data.hour,
            minute=form.start_time.data.minute
        )
        scheduler.add_job(cam_off, "cron",
            id=end_job_id,
            day_of_week=day,
            hour=form.end_time.data.hour,
            minute=form.end_time.data.minute
        )
    except Exception as error:
        return "couldn't add cron jobs", error
    #save job ids in database
    schedule_obj.start_job_id = start_job_id
    schedule_obj.end_job_id = end_job_id
    try:
        db.session.commit()
    except Exception as error:
        return "couldn't add job ids to db", error
    return schedule_obj.day, schedule_obj.start_time


def halt_jobs(recording_id, how):
    recording = db.session.query(Schedule).filter_by(id=recording_id).first()
    db.session.delete(recording)
    job_ids = [recording.start_job_id, recording.end_job_id]
    for job_id in job_ids:
        if how == "remove":
            scheduler.remove_job(job_id)
        elif how == "pause":
            scheduler.pause_job(job_id)
    return recording.day, recording.start_time


def edit_job(form, recording_id):
    #look up schedule objs
    recording = db.session.query(Schedule).filter_by(id=recording_id).first()
    recording.start_time = form.start_time.data
    recording.end_time = form.end_time.data
    start_job = scheduler.get_job(recording.start_job_id)
    end_job = scheduler.get_job(recording.end_job_id)
    start_job.reschedule("cron", day_of_week=recording.day, hour=recording.start_time.hour, minute=recording.start_time.minute)
    end_job.reschedule("cron", day_of_week=recording.day, hour=recording.end_time.hour, minute=recording.end_time.minute)
    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        return error
    return "edit succeeded"


def get_jobs(section_id, state):
    section_schedule = db.session.query(Schedule).filter_by(section_id=section_id)
    if state == "all":
        return section_schedule.all()
    else:
        if state == "active":
            job_ids = [job.id for job in scheduler.get_jobs() if job.next_run_time is not None]
        elif state == "inactive":
            job_ids = [job.id for job in scheduler.get_jobs() if job.next_run_time is None]
        #if there are active or inactive, send them back, if not send an empty list
        if job_ids:
            return section_schedule.filter(Schedule.start_job_id.in_(job_ids)).all()
        else:
            return []
