from flask import Flask
from settings import SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, SQLALCHEMY, UPLOAD_FOLDER, STATIC_FOLDER
 
app = Flask(__name__)
app.secret_key = SECRET_KEY 

#Flask-Mail Settings
app.config["MAIL_SERVER"] = MAIL_SERVER 
app.config["MAIL_PORT"] = MAIL_PORT 
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = MAIL_USERNAME 
app.config["MAIL_PASSWORD"] = MAIL_PASSWORD 

# Flask-SQLAlchemy Settings 
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY 

#File Upload Settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER

#Initialize App with DB and Email
from routes import mail
from models import db
mail.init_app(app)
db.init_app(app)

#INitialize Flask-Admin
from admin import MyHomeView
from flask.ext.admin import Admin 
from flask.ext.admin.contrib.sqla import ModelView
from models import Member, Project, School, Judge, Score, MentorPhoto, PastWinner
admin = Admin(app, index_view=MyHomeView(), name="Pennvention Admin")
admin.add_view(ModelView(Member, db.session))
admin.add_view(ModelView(Project, db.session))
admin.add_view(ModelView(School, db.session))
admin.add_view(ModelView(Judge, db.session))
admin.add_view(ModelView(Score, db.session))
admin.add_view(ModelView(MentorPhoto, db.session))
admin.add_view(ModelView(PastWinner, db.session))
