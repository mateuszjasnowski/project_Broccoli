from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt #copy
from flask_login import LoginManager #copy
from flask_mail import Mail
from appData import brocooliSecrets

app = Flask(__name__)
app.config['SECRET_KEY'] = '1c33f4287204b6e6823d1853e224353d'
#app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_URI']= brocooliSecrets.dbDATABASE_URI
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) #copy
login_manager = LoginManager(app) #copy
login_manager.login_view = 'login' #copy
login_manager.login_message = 'Musisz być zalogowany aby otrzymać dostęp do tej strony!'
login_manager.login_message_category = 'info' #copy
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = brocooliSecrets.emailAddress
app.config['MAIL_PASSWORD'] = brocooliSecrets.emailSecret
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

from appData import routes