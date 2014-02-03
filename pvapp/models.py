#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

Judging = db.Table(
  'judging',
  db.Column('judge_id', db.Integer, db.ForeignKey('judge.id')),
  db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)

Schools = db.Table(
  'schools',
  db.Column('member_id', db.Integer, db.ForeignKey('member.id')),
  db.Column('school_id', db.Integer, db.ForeignKey('school.id'))
)

class PastWinner(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  projectname = db.Column(db.String(100))
  info = db.Column(db.String(1000))
  photo = db.Column(db.String(50))

class MentorPhoto(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  position = db.Column(db.String(100))
  organization = db.Column(db.String(100))
  bio = db.Column(db.String(1000))
  photo = db.Column(db.String(50))
  
class SponsorPhoto(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(25))
  prize = db.Column(db.String(500))
  photo = db.Column(db.String(50))

class School(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(25))
  
  def __init__(self, name):
    self.name = name
  def __repr__(self):
    return '%s' % (self.name)

class Judge(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  specialcode = db.Column(db.String(50))
  name = db.Column(db.String(50))
  email = db.Column(db.String(120), unique=True)  
  pwdhash = db.Column(db.String(100))
  scores = db.relationship('Score', backref='judge', lazy='dynamic')
  reviewing = db.relationship(
    'Project',
    secondary=Judging,
    backref=db.backref('judges', lazy='dynamic')
  )
  def __repr__(self):
    return '%s' % (self.name)
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)
  def setup(self, name, email, password):
    self.name = name
    self.email = email
    self.set_password(password)
  def setjudges(self):
    projects = Project.query.all()
    for each in projects:
      print each.judges.all()
      if len(each.judges.all()) < 4:
        self.reviewing.append(each)
      else:
        print "no new assignments, no no new"
  def __repr__(self):
    return '%s' % (self.name)

class Member(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  email = db.Column(db.String(120), unique=True)  
  phone = db.Column(db.String(20))
  pwdhash = db.Column(db.String(100))
  project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
  level = db.Column(db.String(20))
  year = db.Column(db.Integer)
  education = db.relationship(
    'School', 
    secondary=Schools, 
    backref=db.backref('students', lazy='dynamic')
  )
  
  def __init__(self, name, email, phone, password, education, level, year, project_id):
    self.name = name
    self.email = email.lower()
    self.phone = phone
    self.year = year
    self.project = Project.query.get(project_id)
    self.set_password(password)
    self.level = level
    for school in education:
      if School.query.filter(School.name == school).first():
        existingschool = School.query.filter(School.name == school).first()
        self.education.append(existingschool)
      else:
        newschool = School(school)
        self.education.append(newschool)

  def __repr__(self):
        return '%s' % (self.name)
 
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)

class Score(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  judge_id = db.Column(db.Integer, db.ForeignKey('judge.id'))
  project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
  weighted = db.Column(db.Float) 
  def setup(self, judgeid, projectid, score):
    self.judge_id = judgeid
    self.project_id = projectid
    self.weighted = score
  def __repr__(self):
    return 'Score of %d for %s by %s' % (self.weighted, self.project, self.judge) 

class Project(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  submitted = db.Column(db.DateTime(timezone=True))
  projectname = db.Column(db.String(50))
  description = db.Column(db.String(500))
  phaseone = db.Column(db.String(100))
  members = db.relationship('Member', backref='project', lazy='dynamic') 
  scores = db.relationship('Score', backref='project', lazy='dynamic')
  def __init__(self, projectname, description):
    self.submitted = datetime.now()
    self.projectname = projectname
    self.description = description    
  
  def __repr__(self):
        return 'Project %s' % (self.projectname)

  def submitphaseone(self, phaseone):
    self.phaseone = phaseone
  def updatesubmissiontime(self):
    self.submitted = datetime.now() 
