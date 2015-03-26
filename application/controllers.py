from flask import request, Response, session, escape, redirect, flash
from flask import render_template, send_from_directory, url_for
from application import app
from application import scheduler
from application import schedules
from application.forms import SignupForm, SigninForm, ScheduleForm

# routing for API endpoints (generated from the models designated as API_MODELS)
from application.core import api_manager
from application.models import *

for model_name in app.config['API_MODELS']:
    model_class = app.config['API_MODELS'][model_name]
    api_manager.create_api(model_class, methods=['GET', 'POST'])

api_session = api_manager.session

@app.route('/')
def home():
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email = session['email']).first()
    if user is None:
        return redirect(url_for('signup'))
    else:
        return render_template('home.html')

@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        return request.get_data()
    elif request.method == 'GET':
        return 'hi there'

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
            return redirect(url_for('schedule'))

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

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    form = ScheduleForm()
    if 'email' not in session:
      return redirect(url_for('home'))
    
    if request.method == 'POST':
      if form.validate() == False:
        return render_template('schedule.html', form=form)
      else:
        return '%s, %s, %s - %s' % (form.section.data, form.days.data,form.start_time.data, form.end_time.data)
      #get the day for the date
    if request.method == 'GET':
      return render_template('schedule.html', form=form)

@app.route('/add/<int:TIME>/<JOB_ID>')
def add(TIME, JOB_ID):
  scheduler.add_job(schedules.scheduler_job, 
    'interval', 
    seconds=TIME, 
    id=JOB_ID,
    replace_existing=True)
  return 'job scheduled: %s' %(JOB_ID)

@app.route('/remove/<JOB_ID>')
def remove(JOB_ID):
  scheduler.remove_job(JOB_ID)
  return 'job removed: %s' %(JOB_ID)