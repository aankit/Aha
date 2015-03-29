from flask import request, Response, session, escape, redirect, flash
from flask import render_template, send_from_directory, url_for
from application import scheduler
from application.schedules import cam_start, cam_stop, add_cron
from application.forms import SignupForm, SigninForm, ScheduleForm
from application.models import *


@app.route('/')
def home():
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(email = session['email']).first()
    if user is None:
        return redirect(url_for('signup'))
    else:
        return render_template('home.html', user=user)

# @app.route('/log', methods=['GET', 'POST'])
# def log():
#     if request.method == 'POST':
#         return request.get_data()
#     elif request.method == 'GET':
#         return 'hi there'

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
        
        #store section
        section_obj = Section.query.filter_by(name=form.section.data).first()
        if not section_obj:
          section_obj = Section(name=form.section.data, 
            user_id=db.session.query(User.id).filter_by(email=session['email']).first()[0])
          db.session.add(section_obj)
          db.session.commit()

        #iterate through the days
        for day in form.days.data:
          try:
            print day
            print form.start_time.data
            print form.end_time.data
            #store the times
            schedule_obj = Schedule(day=day, 
              start_time=form.start_time.data, 
              end_time=form.end_time.data, 
              section_id=section_obj.id)
            db.session.add(schedule_obj)
            db.session.commit()
            #create jobs
            start_job = "%d_start" % (schedule_obj.id)
            end_job = "%d_end" % (schedule_obj.id)
            add_cron(cam_start, start_job, day,form.start_time.data.hour,form.start_time.data.minute)
            add_cron(cam_start, end_job, day,form.end_time.data.hour,form.end_time.data.minute)
            #save job ids in database
            start_obj = Job(job_id=start_job, schedule_id=schedule_obj.id)
            stop_obj = Job(job_id=end_job, schedule_id=schedule_obj.id)
            db.session.add(start_obj)
            db.session.add(stop_obj)
            db.session.commit()
          except Exception as e:
            db.session.rollback()
            return render_template("error.html", error=e)

        #redirecting back to schedule page with flash for success
        return redirect(url_for('schedule'))
        # return "check the server console"
    
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

@app.route('/logo')
def logo():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                 'img/aha.png')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404