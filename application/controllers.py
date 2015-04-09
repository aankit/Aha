from flask import request, session, redirect, flash
from flask import render_template, url_for
from application.models import *
from application import app, schedule, api_manager
from application.forms import SignupForm, SigninForm, ScheduleForm
import time

for model_name in app.config['API_MODELS']:
  model_class = app.config['API_MODELS'][model_name]
  api_manager.create_api(model_class, methods=['GET', 'POST'])

@app.route('/')
def home():
  if 'email' not in session:
    return redirect(url_for('signin'))
  user = User.query.filter_by(email = session['email']).first()
  if user is None:
    return redirect(url_for('signup'))
  else:
    return render_template('home.html', user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm()
  if request.method == 'POST':
      if form.validate() == False:
          return render_template('signup.html', form=form)
      else:
          newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
          db.session.add(newuser)
          db.session.commit()
          session['email'] = newuser.email
          return redirect(url_for('add_recording'))

  elif request.method == 'GET':
      return render_template('signup.html', form=form)


@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()
  if 'email' in session:
    return redirect(url_for('home')) 

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('home'))
                 
  elif request.method == 'GET':
    return render_template('signin.html', form=form)


@app.route('/signout')
def signout():
  if 'email' not in session:
    return redirect(url_for('signin'))   
  session.pop('email', None)
  return redirect(url_for('home'))


@app.route('/profile')
def profile():
  if 'email' not in session:
    return redirect(url_for('signin'))
  user = User.query.filter_by(email = session['email']).first()
  if user is None:
    return redirect(url_for('signup'))
  else:
    return render_template('home.html', user=user)

@app.route('/camera')
def live():
  return render_template('live.html')

@app.route('/camera/<state>/')
def camera_on(state):
  print state
  section_id = request.args.get('section_id')
  timestamp_string = request.args.get('timestamp')
  if state == 'on':
    timestamp_obj = time.strptime(timestamp_string, "%Y-%m-%d %H:%M:%S")
    recording_filename = schedule.cam_record(timestamp_obj, section_id)
    return recording_filename
  elif state == 'off':
    recording_filename = schedule.camera.off()
    return recording_filename
  else:
    return 'please send a state of on or off.'
  return "thanks!"

@app.route('/camera/')

@app.route('/schedule')
def view_schedule():
  form = ScheduleForm()
  jobs = schedule.get_scheduled()
  return render_template('schedule.html', 
    jobs=jobs,
    form=form)


@app.route('/recording', methods=['GET', 'POST'])
def add_recording():
  form = ScheduleForm()

  #POST
  if request.method == 'POST' and form.validate():
    section_id = schedule.add_section(form, session)
    if section_id:
      #iterate through the days
      for day in form.days.data:
        try:
          schedule.add_schedule(form, day, section_id)
        except Exception as error:
          db.session.rollback()
          return render_template("error.html", error="%d: %s" % (500, error))
      flash('Success! You have added your recordings.')
      return redirect(url_for('view_schedule'))
    else:
      flash('Section name already taken!')
      return redirect(url_for('view_schedule'))
  #GET
  else:
    return render_template('recording.html', 
      form=form, 
      title = "Add Recording", 
      endpoint='add_recording', 
      name=None)


@app.route('/recording/<id>', methods=['GET', 'POST'])
def edit_recording(id):
  form = ScheduleForm()

  #POST
  if request.method == 'POST' and form.validate():
    section_id=Section.query.filter_by(name=form.section.data).first().id
    status, message = schedule.edit_schedule(form, section_id)
    #respond to the client
    if status == 201:
      flash(message)
      return redirect(url_for('view_schedule'))
    else:
      return render_template("error.html", error="%d: %s" % (status, message))
  #GET
  else:
    d = form.get_data(id)
    if d:
      form.section.data = d['section']
      form.days.data = d['days']
      form.start_time.data =  d['start_time']
      form.start_ampm.data = d['start_ampm']
      form.end_time.data = d['end_time'] 
      form.end_ampm.data = d['end_ampm']
      return render_template('recording.html', 
        title = "Edit Recording", 
        endpoint = 'edit_recording', 
        name = name,
        form = form)
    else:
      return render_template("error.html", error="Class doesn't exist :(")

@app.route('/recording/d/<id>')
def delete_recording(id):
  day, section_name = schedule.delete_schedule(id)
  flash("You have successfully deleted the %d recording for %s" %(day, section_name))
  return redirect(url_for("view_schedule"))

@app.route('/editor')
def editor():
  return render_template("mobile_editor.html")


@app.route('/logo')
def logo():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                 'img/aha.png')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404