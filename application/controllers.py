from flask import request, session, redirect, flash
from flask import render_template, url_for
from application.models import *
from application import app, scheduler, schedule, picam, api_manager
from application.forms import SignupForm, SigninForm, ScheduleForm, SectionForm
from application.filters import dayformat
from datetime import datetime
import json, urllib

for model_name in app.config['API_MODELS']:
    model_class = app.config['API_MODELS'][model_name]
    api_manager.create_api(model_class, methods=['GET', 'POST'])


@app.route('/')
def home():
    if 'email' not in session:
        return redirect(url_for('signin'))

    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return redirect(url_for('signup'))
    else:
        return render_template('home.html', user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate() is False:
            return render_template('signup.html', form=form)
        else:
            newuser = User(form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            session['email'] = newuser.email
            session['id'] = newuser.id
            return redirect(url_for('section'))

    elif request.method == 'GET':
        return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if 'email' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user = form.validate()
        if user is False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = user.email
            session['id'] = user.id
            return redirect(url_for('home'))
    elif request.method == 'GET':
        return render_template('signin.html', form=form)


@app.route('/signout')
def signout():
    if 'email' not in session:
        return redirect(url_for('signin'))
    session.pop('email', None)
    return redirect(url_for('home'))


@app.route('/settings')
def settings():
    if 'email' not in session:
        return redirect(url_for('signin'))
    # here we can configure timezone, teacher observation rubric for scraping


@app.route('/editor')
def editor():
    return render_template("mobile_editor.html")


@app.route('/camera')
def camera():
    state = request.args.get('state')
    schedule_id = request.args.get('schedule_id')
    timestamp_string = request.args.get('timestamp')
    #turn the camera on and return the DB id of the new video
    if state == 'on':
        datetime_timestamp = datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")
        video_id = schedule.cam_record(schedule_id, datetime_timestamp)
        return str(video_id)
    #turn the camera off
    elif state == 'off':
        schedule.cam_off()
        return 'off'
    #return the DB id of the current video being recorded or -1 if no video being recorded.
    elif state == 'current':
        curr_recording = picam.record_state()
        if curr_recording:
            video_obj = db.session.query(Video).filter(Video.filename == curr_recording).one()
            video_id = video_obj.id
        else:
            video_id = -1
        return str(video_id)
    elif state == 'live':
        pid = picam.service_on()
        ret = urllib.urlopen('http://aha.local/hls/index.m3u8')
        while ret.code == 404:
            ret = urllib.urlopen('http://aha.local/hls/index.m3u8')
        return render_template('live.html', pid=json.dumps(pid))
    else:
        return render_template('404.html')


@app.route('/section', methods=['GET', 'POST'])
def section():
    form = SectionForm()
    sections = Section.query.filter_by(user_id=session['id']).all()
    #POST
    if request.method == 'POST' and form.validate(session["id"]):
        section_obj = Section(name=form.name.data,
            user_id=db.session.query(User).filter_by(email=session['email']).first().id)
        db.session.add(section_obj)
        try:
            db.session.commit()
            flash("Successfully added section %s" % (section_obj.name))
        except Exception as error:
            db.session.rollback()
            flash("Database error: %s" % (error))
        return redirect(url_for('section'))
    #GET
    else:
        action = request.args.get('action')
        if action == 'delete':
            section_id = request.args.get('section_id')
            section = Section.query.filter_by(id=section_id).first()
            recordings = schedule.get_jobs(section_id, "all")
            for recording in recordings:
                schedule.halt_jobs(recording.id, "remove")
                db.session.delete(recording)
            db.session.delete(section)
            try:
                db.session.commit()
                flash("Deleted %s" % (section.name))
                return redirect(url_for('section'))
            except Exception as error:
                flash("Database error: %s" % (error))
        return render_template('section.html', sections=sections, form=form)


@app.route('/recordings', methods=['GET', 'POST'])
def recordings():
    form = ScheduleForm()
    section_id = request.args.get("section_id")
    #POST
    if request.method == 'POST' and form.validate():
        #iterate through the days
        for day in form.days.data:
            try:
                day, time = schedule.add_jobs(form, day, section_id)
                flash('Success! You have added a %s recording for %s.' % (dayformat(day), time))
            except Exception as error:
                db.session.rollback()
                flash('There was a database error %s' % (error))
        return redirect(url_for('recordings', section_id=section_id))
    #GET
    else:
        state = request.args.get("state")
        section = Section.query.filter_by(id=section_id).first()
        recording_id = request.args.get("recording_id")
        if state == "activate":
            schedule_obj = Schedule.query.filter_by(id=recording_id).first()
            scheduler.resume_job(schedule_obj.start_job_id)
            scheduler.resume_job(schedule_obj.end_job_id)
            return redirect(url_for('recordings', section_id=section_id))
        if state == "deactivate":
            day, start_time = schedule.halt_jobs(recording_id, "pause")
            flash("You have successfully deactivated %s's %d recording at %s" % (section.name, dayformat(day), start_time))
            return redirect(url_for('recordings', section_id=section_id))
        active_recordings = schedule.get_jobs(section_id, 'active')  # need to make an active and inactive job function & list
        inactive_recordings = schedule.get_jobs(section_id, 'inactive')
        return render_template('schedule.html',
            active_recordings=active_recordings,
            inactive_recordings=inactive_recordings,
            form=form,
            section=section)


@app.route('/recording', methods=['GET', 'POST'])
def recording():
    form = ScheduleForm()
    section_id = request.args.get("section_id")
    section = Section.query.filter_by(id=section_id).first()
    recording_id = request.args.get("recording_id")
    #POST
    if request.method == 'POST' and form.validate(recording_id):
        message = schedule.edit_job(form, recording_id)
        #respond to the client
        flash(message)
        return redirect(url_for('recordings', section_id=section_id))
    #GET
    else:
        schedule_obj = db.session.query(Schedule).filter_by(id=recording_id).first()
        if schedule_obj:
            form.days.data = [schedule_obj.day]
            form.start_time.data = schedule_obj.start_time
            form.end_time.data = schedule_obj.end_time
            return render_template('recording.html',
                section=section,
                id=recording_id,
                form=form)
        else:
            return render_template("error.html", error="Couldn't get data for this recording")


@app.route('/example')
def example():
    return render_template("example.html")


@app.route('/logo')
def logo():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/aha.png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
