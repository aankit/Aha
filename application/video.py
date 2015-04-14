from application.models import *
from application import scheduler
from application import picam
from application import db
from datetime import datetime
import time

def cam_record(schedule_id, start_time=None):
    '''Turns the picam service on if not on,
    starts recording, ending existing recording,
    and saves the new video in DB.

    Returns the video_id, if any.'''
    #create start timestamp if none provided
    if start_time==None:
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
    '''Turns the current picam recording off if recording,
    turns the picam service_off if on'''
    picam_pid = picam.service_state()
    recording_filename = picam.record_state()
    if recording_filename:
        picam.record_off()
    if picam_pid:
        picam.service_off()
    return 0


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
    start_job_id = "section_%d-schedule_%d-start" % (section_id, schedule_obj.id)
    end_job_id = "section_%d-schedule_%d-end" % (section_id, schedule_obj.id)
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
    start_obj = Job(job_id=start_job_id, schedule_id=schedule_obj.id)
    stop_obj = Job(job_id=end_job_id, schedule_id=schedule_obj.id)
    db.session.add(start_obj)
    db.session.add(stop_obj)
    try:
        db.session.commit()
    except Exception as error:
        return "couldn't add jobs to db", error
    return schedule_obj.day, schedule_obj.start_time


def remove_jobs(recording_id):
    schedule_objs = db.session.query(Schedule).filter_by(id=recording_id).all()
    days = []
    times = []
    for schedule_obj in schedule_objs:
        days.append(schedule_obj.day)
        times.append(schedule_obj.start_time)
        jobs = schedule_obj.jobs
        for job in jobs:
            db.session.delete(job)
            try:
                db.session.commit()
                scheduler.remove_job(job.job_id)
            except Exception as error:
                db.session.rollback()  # can get rid of this later
                return error
    return days, times


def edit_jobs(form, section_id, recording_id):
    #look up schedule objs
    recording = db.session.query(Schedule).filter_by(id=recording_id).first()
    #should we keep track of what we are about to do??
    try:
        #modify days already in the database
        if recording.day in form.days.data:
            recording.start_time = form.start_time.data
            recording.end_time = form.end_time.data
            db.session.commit()
        #delete days that the user has not specified in new schedule
        else:
            remove_jobs(recording.id)
        #and add days not in there
        for day in form.days.data:
            if day not in recording.day:
                add_jobs(form, day, section_id)
    except Exception as error:
        db.session.rollback()
        return error
    return "edit succeeded"


def get_jobs(section_id):
    return db.session.query(Schedule).filter_by(section_id=section_id).all()
