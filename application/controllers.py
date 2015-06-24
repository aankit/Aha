from flask import request, session, redirect, flash, g
from flask import render_template, url_for
from application.models import *
from application import app, api_manager
from application.forms import SignupForm, SigninForm, ScheduleForm, InvestigationForm
from camera import control
import sh
import json

for model_name in app.config['API_MODELS']:
    model_class = app.config['API_MODELS'][model_name]
    api_manager.create_api(model_class, methods=['GET', 'POST'])


def commit_to_db(success_msg):
    try:
        db.session.commit()
        flash(success_msg)
        return 1
    except Exception as error:
        db.session.rollback()
        flash("Database error: %s" % (error))
        return 0


@app.before_request
def before_request():
    g.cam_state = control.record_state()


@app.route('/')
def home():
    if 'email' not in session:
        return redirect(url_for('signin'))

    user = User.query.filter_by(email=session['email']).first()
    if user is None:
        return redirect(url_for('signup'))
    else:
        return redirect(url_for('investigation'))


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
            return redirect(url_for('investigation'))

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


@app.route('/capture')
def capture():
    return render_template("mobile_editor.html")

@app.route('/demo')
def demo():
    return render_template("show.html")


# need to transfer control of this to camera module
@app.route('/camera')
def camera():
    state = request.args.get('state')
    #turn the camera on and return the DB id of the new video
    if state == 'on':
        if control.service_state() is False:
            control.service_on()
            sh.sleep(1)
        control.record_on()
        g.cam_state = 'on'
        return redirect(url_for('home'))
    #turn the camera off
    elif state == 'off':
        control.record_off()
        g.cam_state = 'off'
        return redirect(url_for('home'))
    elif state == 'state':
        return control.record_state()
    elif state == 'live':
        return render_template('live.html')
    else:
        return render_template('404.html')


@app.route('/investigation', methods=['GET', 'POST'])
def investigation():
    form = InvestigationForm()
    #POST
    if request.method == 'POST' and form.validate(session['id']):
        investigation_obj = Investigation(question=form.question.data.strip(),
                                          user_id=session['id'])
        db.session.add(investigation_obj)
        if commit_to_db("Successfully added investigation %s" % (investigation_obj.question)):
            #make a directory for the new investigation's videos
            user = User.query.filter_by(email=session['email']).first()
            sh.mkdir(user.media_url + '/' + str(investigation_obj.id))
        return redirect(url_for('investigation'))
    #GET
    else:
        action = request.args.get('action')
        if action == 'delete':
            investigation_id = request.args.get('investigation_id')
            investigation = Investigation.query.filter_by(id=investigation_id).first()
            recordings = db.session.query(Schedule).filter_by(investigation_id=investigation_id).all()
            #delete the recordings in the database
            for recording in recordings:
                db.session.delete(recording)
            #delete the investigations in the database
            db.session.delete(investigation)
            if commit_to_db("Deleted %s" % (investigation.question)):
                user = User.query.filter_by(email=session['email']).first()
                #remove the media directory for the investigation
                sh.rm('-rf', ('/').join([str(user.media_url), str(investigation_id)]))
        #return list of investigations
        investigations = Investigation.query.filter_by(user_id=session['id']).all()
        return render_template('investigation.html', investigations=investigations, form=form)


@app.route('/recordings', methods=['GET', 'POST'])
def recordings():
    form = ScheduleForm()
    investigation_id = request.args.get("investigation_id")
    #POST
    if request.method == 'POST' and form.validate():
        for day in form.days.data:
            #store the times
            schedule_obj = Schedule(day=day,
                                    active=True,
                                    start_time=form.start_time.data,
                                    end_time=form.end_time.data,
                                    investigation_id=investigation_id)
            db.session.add(schedule_obj)
        if commit_to_db('Success! You have added a recording.'):
            user = User.query.filter_by(email=session['email']).first()
            media_url = ('/').join([str(user.media_url), str(investigation_id), str(schedule_obj.id)])
            print media_url
            sh.mkdir(media_url)
        return redirect(url_for('recordings', investigation_id=investigation_id))
    #GET
    else:
        state = request.args.get("state")
        investigation = Investigation.query.filter_by(id=investigation_id).first()
        recording_id = request.args.get("recording_id")
        if state == "activate":
            schedule_obj = db.session.query(Schedule).filter_by(id=recording_id).first()
            schedule_obj.active = True
            commit_to_db("You have successfully activated a recording.")
            return redirect(url_for('recordings', investigation_id=investigation_id))
        if state == "deactivate":
            schedule_obj = db.session.query(Schedule).filter_by(id=recording_id).first()
            schedule_obj.active = False
            commit_to_db("You have successfully deactivated a recording.")
            return redirect(url_for('recordings', investigation_id=investigation_id))
        active_recordings = db.session.query(Schedule) \
            .filter_by(investigation_id=investigation_id) \
            .filter_by(active=True).all()
        inactive_recordings = db.session.query(Schedule) \
            .filter_by(investigation_id=investigation_id) \
            .filter_by(active=False).all()
        return render_template('schedule.html',
                               active_recordings=active_recordings,
                               inactive_recordings=inactive_recordings,
                               form=form,
                               investigation=investigation)


@app.route('/recording', methods=['GET', 'POST'])
def recording():
    form = ScheduleForm()
    investigation_id = request.args.get("investigation_id")
    investigation = Investigation.query.filter_by(id=investigation_id).first()
    recording_id = request.args.get("recording_id")
    #POST
    if request.method == 'POST' and form.validate(recording_id):
        recording = db.session.query(Schedule).filter_by(id=recording_id).first()
        recording.start_time = form.start_time.data
        recording.end_time = form.end_time.data
        commit_to_db("Edit succeeded")
        return redirect(url_for('recordings', investigation_id=investigation_id))
    #GET
    else:
        schedule_obj = db.session.query(Schedule).filter_by(id=recording_id).first()
        if schedule_obj:
            form.days.data = [schedule_obj.day]
            form.start_time.data = schedule_obj.start_time
            form.end_time.data = schedule_obj.end_time
            return render_template('recording.html',
                                   investigation=investigation,
                                   id=recording_id,
                                   form=form)
        else:
            return render_template("error.html", error="Couldn't get data for this recording")


@app.route('/videos')
def videos():
    obj_type = request.args.get("obj_type") if request.args.get("obj_type") else None
    obj_id = request.args.get("obj_id") if request.args.get("obj_id") else None
    return render_template("videos.html", obj_type=json.dumps(obj_type), obj_id=json.dumps(obj_id))


@app.route('/video/<format>/<int:vid>')
def video(format, vid):
    video = Video.query.filter_by(id=vid).all()
    if format == "stub":
        return render_template("video_stub.html", video=video)
    else:
        return render_template("video.html", video=video)


@app.route('/move/<direction>')
def move(direction):
    #we need to check the database for current position
    #move the camera based on the current position
    #update the database with the new position
    return "OK"


@app.route('/logo')
def logo():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/aha.png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
