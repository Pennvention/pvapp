from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms import validators, ValidationError, TextField, TextAreaField, SubmitField, PasswordField, SelectMultipleField, FormField
from models import Member, db, Judge

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

class NewMember(Form):
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = EmailField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
  education = SelectMultipleField('School', choices=[('SEAS Undergrad', 'SEAS Undergrad Student'), ('SEAS Grad', 'SEAS Grad Student'), ('Wharton Undergrad', 'Wharton Undergrad Student'), ('Wharton Grad', 'Wharton MBA Student'), ('SAS Undergrad', 'SAS Student'), ('Nursing', 'Nursing Student')]) 
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
      newproject = Project(form.projectname.data, form.description.data)
      db.session.add(newproject)
      db.session.commit()
      firstmember = Member(self.firstmember.data['name'], self.firstmember.data['email'], self.firstmember.data['password'], self.firstmember.data['education'], newproject.id)
      db.session.add(firstmember)
      db.session.commit()
      return True

class AddMemberForm(Form):
  newmember = FormField(NewMember) 
  submit = SubmitField("Send") 

class PhaseOneForm(Form):
  presentation = FileField('Presentation in PDF Format', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
  submit = SubmitField("Send")

class CreateProjectForm(Form):
  projectname = TextField("Project Name", [validators.Required("Please enter a name for your project.")])
  description = TextAreaField("Short Project Description", [validators.Required("Please enter a description for your project.")]) 
  firstmember = FormField(NewMember)
  submit = SubmitField("Send")
  def getproject(self):
    return Project.query.filter_by(projectname = self.projectname).first().id


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
    else:
      self.email.errors.append("Invalid e-mail or password")
      return False 
