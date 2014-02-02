#!/usr/bin/python
# -*- coding: utf-8 -*-
# from __future__ imports must be done at top
from __future__ import division
import os
from pvapp import app
from flask import render_template, request, flash, session, url_for, redirect, send_from_directory
from forms import ContactForm, SigninForm, CreateProjectForm, AddMemberForm, PhaseOneForm, AddJudgeForm
from flask.ext.mail import Message, Mail
from models import db, Project, Member, Judge, MentorPhoto, PastWinner 
from functools import wraps
from werkzeug import secure_filename

mail = Mail()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if ('project' not in session) and ('judge' not in session):
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

@app.route('/')
def home():
  static = app.config['UPLOAD_FOLDER']
  mentors = MentorPhoto.query.all()
  pastwinners = PastWinner.query.all()
  return render_template('index.html', pastwinners=pastwinners, mentors=mentors, home="yes")

@app.route('/home')
def homepage():
  login = SigninForm() 
  return render_template('home.html', login=login)

@app.route('/about')
def about():
  login = SigninForm() 
  return render_template('about.html', login)

@app.route('/isjudge')
def isjudge():
  if 'judge' in session:
    return "You're a judge!"
  return "Nope, you're not a judge."

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
  login = SigninForm() 
  form = CreateProjectForm()
  if form.validate_on_submit():
    session['project'] = form.getproject() 
    flash('You successfully created your project. You may now add the rest of your project members.')
    return redirect(url_for('profile'))
  return render_template('register.html', form=form, login=login) 

@app.route('/addmember', methods=['GET', 'POST'])
@project_view
def addmember():
  form = AddMemberForm()
  if form.validate_on_submit():
    newmember = Member(form.newmember.data['name'], form.newmember.data['email'], form.newmember.data['password'], form.newmember.data['education'], session['project'])
    db.session.add(newmember)
    db.session.commit()
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
    return redirect(url_for('profile'))
  flash('Incorrect login details. Please try again or register for a new account.')
  return redirect(url_for('home')) 

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
  else:
    j = Judge.query.get(session['judge'])
    return render_template('judgeprofile.html', j=j)

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

@app.route('/static/<filename>')
def uploads(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)

@app.route('/signout')
@login_required
def signout():
  session.pop('project', None)
  session.pop('judge', None)
  return redirect(url_for('home'))

<<<<<<< HEAD
=======
if __name__ == '__main__':
  	app.run(host='0.0.0.0')
>>>>>>> 4ff288696395d0d2b71108f913492782d61ffb84
