from flask import request, session, redirect, flash
from flask import render_template, url_for
from application.models import *
from application import app, schedule, api_manager
from application.forms import SignupForm, SigninForm, ScheduleForm

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

@app.route('/camera')
def live():
  return render_template('live.html')

@app.route('/schedule')
def view_schedule():
  form = ScheduleForm()
  jobs = schedule.get_scheduled()
  return render_template('schedule.html', 
    jobs=jobs,
    form=form)


@app.route('/profile')
def profile():
  if 'email' not in session:
    return redirect(url_for('signin'))
  user = User.query.filter_by(email = session['email']).first()
  if user is None:
    return redirect(url_for('signup'))
  else:
    return render_template('home.html', user=user)


@app.route('/recording', methods=['GET', 'POST'])
def add_recording():
  form = ScheduleForm()

  #POST
  if request.method == 'POST' and form.validate():
    status, message = schedule.add_schedule(form, session)  
    #respond to the client
    if status == 201:
      flash(message)
      return redirect(url_for('add_recording'))
    else:
      render_template("error.html", error="%d: %s" % (status, message))
  #GET
  else:
    return render_template('recording.html', 
      form=form, 
      title = "Add Recording", 
      endpoint='add_recording', 
      name=None)


@app.route('/recording/<name>', methods=['GET', 'POST'])
def edit_recording(name):
  form = ScheduleForm()

  #POST
  if request.method == 'POST' and form.validate():
    status, message = schedule.edit_schedule(form, session)
    #respond to the client
    if status == 201:
      flash(message)
      return redirect(url_for('schedule'))
    else:
      return render_template("error.html", error="%d: %s" % (status, message))
  #GET
  else:
    d = form.get_data(name)
    if d:
      return render_template('recording.html', 
        title = "Edit Recording", 
        endpoint = 'edit_recording', 
        name = name,
        form=ScheduleForm(section = d['section'], 
          days = d['days'], 
          start_time =  d['start_time'], 
          start_ampm = d['start_ampm'], 
          end_time = d['end_time'], 
          end_ampm = d['end_ampm']))
    else:
      return render_template("error.html", error="Class doesn't exist :(")


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