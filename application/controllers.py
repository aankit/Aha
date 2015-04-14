from flask import request, session, redirect, flash
from flask import render_template, url_for
from application.models import *
from application import app, video, picam, api_manager
from application.forms import *
from datetime import datetime

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
    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return redirect(url_for('signup'))
    else:
        return render_template('home.html', user=user)


@app.route('/camera')
def camera():
    state = request.args.get('state')
    schedule_id = request.args.get('schedule_id')
    timestamp_string = request.args.get('timestamp')
    #turn the camera on and return the DB id of the new video
    if state == 'on':
        datetime_timestamp = datetime.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")
        video_id = video.cam_record(schedule_id, datetime_timestamp)
        return str(video_id)
    #turn the camera off
    elif state == 'off':
        video.cam_off()
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
        return render_template('live.html')
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
            flash("Successly added section %s" % (section_obj.name))
        except Exception as error:
            db.session.rollback()
            flash("Database error: %s" % (error))
        return redirect(url_for('section'))
    #GET
    else:
        action = request.args.get('action')
        section_id = request.args.get('section_id')
        section = Section.query.filter_by(id=section_id).first()
        if action == 'delete':
            recordings = video.get_jobs(section_id)
            for recording in recordings:
                video.remove_jobs(recording.id)
                db.session.delete(recording)
            db.session.delete(section)
            try:
                db.session.commit()
                flash("Deleted %s" % (section.name))
                return redirect(url_for('section'))
            except Exception as error:
                flash("Database error: %s" % (error))
        return render_template('section.html', sections=sections, form=form)


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = newScheduleForm()
    state = request.args.get("action")
    section_id = request.args.get("section_id")
    section = Section.query.filter_by(id=section_id).first()
    recordings = video.get_jobs(section_id)  #need to make an active and inactive job function & list
    #POST
    if request.method == 'POST' and form.validate():
        #iterate through the days
        print form.start_time.data.hour
        print form.end_time.data.hour
        for day in form.days.data:
            try:
                d1, d2 = video.add_jobs(form, day, section_id)
                flash('Success! You have added a %s recording for %s.' % (str(d1), str(d2)))
            except Exception as error:
                db.session.rollback()
                flash('There was a database error %s' % (error))
        return redirect(url_for('schedule', section_id=section_id))
    #GET
    else:
        if state == "deactivate":
            recording_id = request.args.get("recording_id")
            day, start_time = video.remove_jobs(recording_id)
            flash("You have successfully deactivated %s's %d recording at %s" % (section.name, day, start_time))
            return redirect(url_for("schedule"))
        return render_template('schedule.html', recordings=recordings, form=form, section=section)


@app.route('/recording', methods=['GET', 'POST'])
def recording():
    form = newScheduleForm()
    section_id = request.args.get("section_id")
    section = Section.query.filter_by(id=section_id).first()
    recording_id = request.args.get("recording_id")
    #POST
    if request.method == 'POST' and form.validate():
        message = video.edit_jobs(form, recording_id)
        #respond to the client
        flash(message)
        return redirect(url_for('schedule', section_id=section_id))
    #GET
    else:
        d = form.get_data(recording_id)
        if d:
            form.days.data = d['days']
            form.start_time.data = d['start_time']
            form.end_time.data = d['end_time']
            return render_template('recording.html',
                section=section,
                id=recording_id,
                form=form)
        else:
            return render_template("error.html", error="Couldn't get data for this recording")


@app.route('/editor')
def editor():
    return render_template("mobile_editor.html")


@app.route('/example')
def example():
    return render_template("example.html")


@app.route('/logo')
def logo():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/aha.png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
