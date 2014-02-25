#!/usr/bin/python
# -*- coding: utf-8 -*-
# from __future__ imports must be done at top
from __future__ import division
import os, sys
import binascii
import random
from pvapp import app
from flask import render_template, request, flash, session, url_for, redirect, send_from_directory
from forms import ContactForm, SigninForm, CreateProjectForm, AddMemberForm, PhaseOneForm, AddJudgeForm, AddScoreForm
from flask.ext.mail import Message, Mail
from models import db, Project, Member, Judge, MentorPhoto, PastWinner, FrequentlyAsked, Sponsors, Score
from functools import wraps
from werkzeug import secure_filename


mail = Mail()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (('admin' in session) or ('project' in session) or ('judge' in session)):
            flash('Please first login.')
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def project_view(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'judge' in session:
          flash('That page is only for competitors. Sorry about that!')
          return redirect(url_for('profile'))
        if 'project' not in session:
            flash('Please first login.')
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def judge_view(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'judge' not in session:
            flash('You must be a judge to access this page.')
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_view(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash('You must be an admin to access this page.')
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
  static = app.config['UPLOAD_FOLDER']
  mentors = MentorPhoto.query.all()
  pastwinners = PastWinner.query.all()
  faqs = FrequentlyAsked.query.all()
  sponsors = Sponsors.query.all()
  return render_template('index.html', faqs=faqs, pastwinners=pastwinners, mentors=mentors, sponsors=sponsors, home="yes")

@app.route('/about')
def about():
  login = SigninForm() 
  return render_template('about.html', login=login)

@app.route('/addjudges')
@admin_view
def addjudges():
  for n in xrange(25):
    specialcode = binascii.b2a_hex(os.urandom(25))
    newjudge = Judge(specialcode)
    db.session.add(newjudge)
    db.session.commit()
    thisjudge = Judge.query.filter_by(specialcode = specialcode).first()
    thisjudge.setjudges()
  return "Done!"

@app.route('/5projects')
@admin_view
def fiveproj():
  projects = Project.query.all()
  random.shuffle(projects)
  judges = Judge.query.all()
  for judge in judges:
    for each in projects:
      if (len(each.judges.all()) < 6) and (len(judge.reviewing) < 6):
        judge.reviewing.append(each)
        db.session.commit()
      else:
        print "no new assignments, no no new"
  return "Done!"

@app.route('/login')
def login():
  loginform = SigninForm()
  return render_template('login.html', loginform=loginform)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  login = SigninForm() 
  form = ContactForm()
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form, login=login)
    else:
      msg = Message(form.subject.data, sender='contact@example.com', recipients=['nakavthekar@gmail.com'])
      msg.body = """
      From: %s <%s>
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)
      return render_template('contact.html', success=True, login=login)
  elif request.method == 'GET':
    return render_template('contact.html', form=form, login=login)

@app.route('/judgeregister', methods=['GET', 'POST'])
def judgeregister():
  login = SigninForm()
  form = AddJudgeForm()
  if form.validate_on_submit():
    session['judge'] = form.getjudge() 
    flash('You successfully registered as a Judge. Thanks for contributing to entrepreneurship at Penn!')
    return redirect(url_for('profile'))
  return render_template('registerjudge.html', form=form, login=login)

@app.route('/register', methods=['GET', 'POST'])
def register():
  if (('judge' in session) or ('admin' in session) or ('project' in session)):
    redirect(url_for('profile')) 
  login = SigninForm() 
  form = CreateProjectForm()
  if form.validate_on_submit():
    session['project'] = form.getproject() 
    flash('Congratulations! You successfully created your project. You can add the rest of your project members from "Actions" -> "Add Member".')
    return redirect(url_for('profile'))
  return render_template('register.html', form=form, login=login) 

@app.route('/judge/<int:project_id>', methods=['GET', 'POST'])
@judge_view
def judge_project(project_id):
  form = AddScoreForm()
  p = Project.query.get(project_id)
  if form.validate_on_submit():
    researchscore = form.newscore.data['researchscore']
    innovationscore = form.newscore.data['innovationscore']
    planscore = form.newscore.data['planscore']
    comment = form.newscore.data['comment']
    newscore = Score(session['judge'], project_id, researchscore, innovationscore, planscore, comment)
    db.session.add(newscore)
    db.session.commit()
    flash('You have successfully submitted a score!')
    return redirect(url_for('profile'))
  hasnotreviewed = 1
  for score in Score.query.filter_by(project_id = project_id).all():
    if (score.judge_id == session['judge']):
      hasnotreviewed = 0  
  if (Project.query.get(project_id) not in Judge.query.get(session['judge']).reviewing) and hasnotreviewed:
    j = Judge.query.get(session['judge'])
    flash('You did not have permission to view that project. Please select from the projects below that were assigned to you to judge.')
    return redirect(url_for('profile'))
  if not hasnotreviewed:
    flash('You have already reviewed this submission. If you believe this is in error, please email the judging coordinator at pennvention@gmail.com')
    return redirect(url_for('profile'))
  return render_template('judge.html', form=form, p=p, project_id=project_id)

@app.route('/addmember', methods=['GET', 'POST'])
@project_view
def addmember():
  form = AddMemberForm()
  if form.validate_on_submit():
    flash('You have successfully added a member!')
    return redirect(url_for('profile'))
  return render_template('addmember.html', form=form)  

@app.route('/signin', methods=['POST'])
def signin():
  login = SigninForm() 
  if ('project' in session) or ('judge' in session):
    return redirect(url_for('profile')) 
  if login.validate_on_submit(): # means that user is either judge or project member 
    if login.findmember():
      session['project'] = login.getproject() # sets to id of project 
    elif login.findjudge():
      session['judge'] = login.findjudge() # sets to id of judge
    elif login.findadmin():
      session['admin'] = login.findadmin()
    return redirect(url_for('profile'))
  flash('Incorrect login details. Please try again or register for a new account.')
  return redirect(url_for('login')) 

@app.route('/profile')
@login_required
def profile():
  if 'project' in session:
    p = Project.query.get(session['project'])
    members = p.members.all()
    scores = [s.weighted for s in p.scores.all()] 
    if len(scores):
      print sum(scores)/len(scores)
    return render_template('profile.html', p = p, members=members)
  elif 'judge' in session:
    j = Judge.query.get(session['judge'])
    return render_template('judgeprofile.html', j=j)
  elif 'admin' in session:
    projects = Project.query.all();
    return render_template('adminprofile.html', projects=projects)

@app.route('/phaseone/', methods=('GET', 'POST'))
@project_view
def phaseone():
  form = PhaseOneForm()
  if form.validate_on_submit():
    filename = secure_filename(form.presentation.data.filename)
    form.presentation.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    p = Project.query.get(session['project'])
    p.submitphaseone(filename) 
    p.updatesubmissiontime()
    db.session.commit()
    flash("You have successfully submitted your Round 1 Presentation! Stay tuned for judging results, which should arrive in approximately 2 weeks.")
    return redirect(url_for('profile'))
  filename = None
  return render_template('phaseone.html', form=form, filename=filename) 

@app.route('/submission/<filename>') 
def submission(filename): 
  return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)

@app.route('/signout')
@login_required
def signout():
  session.pop('project', None)
  session.pop('judge', None)
  session.pop('admin', None)
  return redirect(url_for('home'))

if __name__ == '__main__':
  	app.run(host='0.0.0.0')
