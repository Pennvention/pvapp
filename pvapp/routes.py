#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from pvapp import app
from flask import render_template, request, flash, session, url_for, redirect, send_from_directory
from forms import ContactForm, SigninForm, CreateProjectForm, AddMemberForm, PhaseOneForm
from flask.ext.mail import Message, Mail
from models import db, Project, Member
from functools import wraps
from werkzeug import secure_filename

mail = Mail()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'project' not in session:
            flash('Please first create a project.')
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:
      msg = Message(form.subject.data, sender='contact@example.com', recipients=['nakavthekar@gmail.com'])
      msg.body = """
      From: %s <%s>
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)

      return render_template('contact.html', success=True)
  elif request.method == 'GET':
    return render_template('contact.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = CreateProjectForm()
  if form.validate_on_submit():
    newproject = Project(form.projectname.data, form.description.data)
    db.session.add(newproject)
    db.session.commit()
    firstuser = Member(form.name.data, form.email.data, form.password.data, newproject.id)
    db.session.add(firstuser)
    db.session.commit()
    session['project'] = newproject.id
    flash('You successfully created your project. You may now add the rest of your project members.')
    return redirect(url_for('addmember'))
  return render_template('register.html', form=form) 

@app.route('/addmember', methods=['GET', 'POST'])
@login_required
def addmember():
  form = AddMemberForm()
  if form.validate_on_submit():
    newmember = Member(form.name.data, form.email.data, form.password.data, session['project'])
    db.session.add(newmember)
    db.session.commit()
    flash('You have successfully added a member')
    return redirect(url_for('home'))
  return render_template('addmember.html', form=form)  

@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()
  if 'project' in session:
    return redirect(url_for('profile')) 
  if form.validate_on_submit(): 
    m = Member.query.filter_by(email = form.email.data.lower()).first()
    p = m.project
    session['project'] = p.id 
    return redirect(url_for('profile'))
  return render_template('signin.html', form=form) 

@app.route('/profile')
@login_required
def profile():
  p = Project.query.get(session['project'])
  members = p.members.all()
  return render_template('profile.html', pname = p.projectname, desc = p.description, members=members)

@app.route('/phaseone/', methods=('GET', 'POST'))
@login_required
def phaseone():
  form = PhaseOneForm()
  if form.validate_on_submit():
    filename = secure_filename(form.presentation.data.filename)
    form.presentation.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print "good" 
    return redirect(url_for('uploads', filename=filename))
  filename = None
  print filename, "hi"
  return render_template('phaseone.html', form=form, filename=filename) 

@app.route('/uploads/<filename>')
@login_required
def uploads(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename)

@app.route('/signout')
@login_required
def signout():
  session.pop('project', None)
  return redirect(url_for('home'))

if __name__ == '__main__':
  	app.run(debug=True)
