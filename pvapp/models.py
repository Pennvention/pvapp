#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug import generate_password_hash, check_password_hash
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

judges = db.Table(
  'judges',
  db.Column('judge_id', db.Integer, db.ForeignKey('judge.id')),
  db.Column('project_id', db.Integer, db.ForeignKey('project.id'))
)
class Member(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(100))
  project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
  
  def __init__(self, name, email, password, project_id):
    self.name = name
    self.email = email.lower()
    self.project = Project.query.get(project_id)
    self.set_password(password)
  
  def __repr__(self):
        return '<Member %r>' % (self.name)
 
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)

class Project(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  submitted = db.Column(db.DateTime(timezone=True))
  projectname = db.Column(db.String(50))
  description = db.Column(db.String(500))
  phaseone = db.Column(db.String(100))
  members = db.relationship('Member', backref='project', lazy='dynamic') 
  judges = db.relationship(
    'Judge', 
    secondary=judges, 
    backref=db.backref('projects', lazy='dynamic')
  )
  def __init__(self, projectname, description):
    self.submitted = datetime.now()
    self.projectname = projectname
    self.description = description    
  
  def __repr__(self):
        return '<Project %r>' % (self.projectname)

  def submitphaseone(self, phaseone):
    self.phaseone = phaseone

class Judge(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
