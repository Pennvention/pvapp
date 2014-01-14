from flask import Flask
from settings import SECRET_KEY, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, SQLALCHEMY
 
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

#Initialize App with DB and Email
from routes import mail
from models import db
db.init_app(app)
mail.init_app(app)
