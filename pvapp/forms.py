from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf.file import FileField, FileRequired, FileAllowed
from wtforms import validators, ValidationError, TextField, TextAreaField, SubmitField, PasswordField
from models import Member, db

class PhaseOneForm(Form):
  presentation = FileField('Presentation in PDF Format', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
  submit = SubmitField("Send")

class CreateProjectForm(Form):
  projectname = TextField("Project Name", [validators.Required("Please enter a name for your project.")])
  description = TextAreaField("Short Project Description", [validators.Required("Please enter a description for your project.")]) 
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = EmailField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  pwdcheck = PasswordField('Re-type Password', [validators.Required("Please re-type your password.")])
  submit = SubmitField("Send")

  def validate(self):
    if not Form.validate(self):
      return False
    member = Member.query.filter_by(email = self.email.data.lower()).first()
    if member:
      self.email.errors.append("That email is already taken")
      return False
    elif self.pwdcheck.data != self.password.data:
      self.password.errors.append("Please retype your password - they didn't match")
      return False 
    else:
      return True


class AddMemberForm(Form):
  name = TextField("Name", [validators.Required("Please enter your name.")])
  email = EmailField("Email", [validators.Required("Please enter your email address."), validators.Email("Please enter a valid email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  pwdcheck = PasswordField('Re-type Password', [validators.Required("Please re-type your password.")])
  submit = SubmitField("Send")
     
  def validate(self):
    if not Form.validate(self):
      return False
    member = Member.query.filter_by(email = self.email.data.lower()).first()
    if member:
      self.email.errors.append("That email is already taken")
      return False
    elif self.pwdcheck.data != self.password.data:
      self.password.errors.append("Please retype your password - they didn't match")
      return False 
    else:
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
   
  def validate(self):
    if not Form.validate(self):
      return False
    member = Member.query.filter_by(email = self.email.data.lower()).first()
    if member and member.check_password(self.password.data):
      return True
    else:
      self.email.errors.append("Invalid e-mail or password")
      return False 
