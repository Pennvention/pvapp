from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms import validators, ValidationError, TextField, TextAreaField, SubmitField, PasswordField, SelectMultipleField, FormField, SelectField
from flask import session
from models import Member, db, Judge, Project
from settings import ADMIN_EMAIL, ADMIN_PASS

class NewJudge(Form):
  specialcode = TextField("Special Code", [validators.Required("Please enter the special code we sent you in an email.")])
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = EmailField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  pwdcheck = PasswordField('Re-type Password', [validators.Required("Please re-type your password.")])
  def validate(self):
    if not Form.validate(self):
      return False
    if self.pwdcheck.data != self.password.data:
      self.password.errors.append("Please retype your password - they didn't match")
      return False 
    checkmember = Member.query.filter_by(email = self.email.data.lower()).first()
    checkjudge = Judge.query.filter_by(email = self.email.data.lower()).first()
    if checkmember or checkjudge: # check if email is already taken 
      self.email.errors.append("That email is already taken")
      return False
    judge = Judge.query.filter_by(specialcode = self.specialcode.data).first() #check if judge specialcode is right
    if judge:
      judge.setup(self.name.data, self.email.data.lower(), self.password.data)
      db.session.commit()
      return True 
    return False

class AddJudgeForm(Form):
  newjudge = FormField(NewJudge)
  submit = SubmitField("Send")
  def getjudge(self):
    return Judge.query.filter_by(name = self.newjudge.data['name']).first().id

scorechoices = [(1, '1 (Lowest Score)'), (2, '2'), (3, '3'), (4, '4'),
		(5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'),
		(10, '10 (Highest Score)')]
					
class NewScore(Form):
  researchscore = SelectField('Research Score', coerce=int, choices=scorechoices, validators=[validators.Required("Please enter a Research Score for this submission")]) 
  innovationscore = SelectField('Innovation Score', coerce=int, choices=scorechoices, validators=[validators.Required("Please enter an Innovation Score for this submission")]) 
  planscore = SelectField('Implementation Plan Score', coerce=int, choices=scorechoices, validators=[validators.Required("Please enter an Implementation Plan Score for this submission")]) 
  comment = TextAreaField("Comment (optional)", description="Limit 2000 Characters")
  
  
class AddScoreForm(Form):
  newscore = FormField(NewScore)
  submit = SubmitField("Send")

class NewMember(Form):
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = EmailField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
  phone = TextField('Phone Number', [validators.Required("Please enter your phone number.")], description="XXX-XXX-XXXX")
  education = SelectMultipleField('School', description='Select all applicable.', choices=[('SEAS', 'SEAS Student'), ('Wharton', 'Wharton Student'), ('SAS', 'SAS Student'), ('Nursing', 'Nursing Student')]) 
  level = SelectField('Level of Study', choices=[('Undergraduate', 'Undergraduate'), ('Graduate', 'Graduate'), ('Doctoral', 'Doctoral')])
  year = SelectField('Year', choices=[('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017'), ('2018', '2018')])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  pwdcheck = PasswordField('Re-type Password', [validators.Required("Please re-type your password.")])
  
  def __init__(self, csrf_enabled=False, *args, **kwargs):
    super(NewMember, self).__init__(csrf_enabled=False, *args, **kwargs)     
  def validate(self):
    if not Form.validate(self):
      return False
    if self.pwdcheck.data != self.password.data:
      self.password.errors.append("Please retype your password - they didn't match")
      return False 
    member = Member.query.filter_by(email = self.email.data.lower()).first()
    if member:
      self.email.errors.append("That email is already taken")
      return False
    else:
      return True

class AddMemberForm(Form):
  newmember = FormField(NewMember) 
  submit = SubmitField("Send") 
  def validate(self):
    if not Form.validate(self):
      return False
    newperson = Member(self.newmember.data['name'], self.newmember.data['email'], self.newmember.data['phone'], self.newmember.data['password'], self.newmember.data['education'], self.newmember.data['level'], self.newmember.data['year'], session['project'])
    db.session.add(newperson)
    db.session.commit()
    return True

class PhaseOneForm(Form):
  presentation = FileField('Presentation in PDF Format', validators=[FileRequired(), FileAllowed(['pdf'], 'Please upload in PDF format.')])
  submit = SubmitField("Send")

class CreateProjectForm(Form):
  projectname = TextField("Project Name", [validators.Required("Please enter a name for your project.")])
  description = TextAreaField("Short Project Description", [validators.Required("Please enter a description for your project.")], description="Limit 500 characters") 
  firstmember = FormField(NewMember)
  submit = SubmitField("Send")
  def getproject(self):
    project = Project.query.filter_by(projectname = self.projectname.data).first()
    return project.id
  def validate(self):
    if not Form.validate(self):
      return False
    newproject = Project(self.projectname.data, self.description.data)
    db.session.add(newproject)
    db.session.commit()
    firstmember = Member(self.firstmember.data['name'], self.firstmember.data['email'], self.firstmember.data['phone'], self.firstmember.data['password'], self.firstmember.data['education'], self.firstmember.data['level'], self.firstmember.data['year'], newproject.id)
    db.session.add(firstmember)
    db.session.commit()
    return True

class ContactForm(Form):
  name = TextField("Name",  [validators.Required("Please enter your name.")])
  email = EmailField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  subject = TextField("Subject",  [validators.Required("Please enter a subject.")])
  message = TextAreaField("Message",  [validators.Required("Please enter a message.")])
  submit = SubmitField("Send")

class SigninForm(Form):
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Sign In")

  # returns member only if password is correct 
  def findmember(self):
    member = Member.query.filter_by(email = self.email.data.lower()).first()
    if member and member.check_password(self.password.data):
      return member 
    return None 
  
  # returns admin email
  def findadmin(self):
    if (self.email.data.lower() == ADMIN_EMAIL) and (self.password.data == ADMIN_PASS):
      return self.email.data.lower()
    return None
  
  # returns project id if member is found
  def getproject(self):
    member = self.findmember() 
    if member:
      project = member.project 
      return project.id
    else:
      return None 

  def findjudge(self):
    judge = Judge.query.filter_by(email = self.email.data.lower()).first()
    if judge and judge.check_password(self.password.data):
      return judge.id
    return None

  def validate(self):
    if not Form.validate(self):
      return False
    if self.findmember(): 
      return True
    elif self.findjudge():
      return True
    elif self.findadmin():
      return True
    else:
      self.email.errors.append("Invalid e-mail or password")
      return False 
