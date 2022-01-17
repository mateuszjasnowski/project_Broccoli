from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt #copy
from flask_login import LoginManager #copy

app = Flask(__name__)
app.config['SECRET_KEY'] = '1c33f4287204b6e6823d1853e224353d'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) #copy
login_manager = LoginManager(app) #copy
login_manager.login_view = 'login' #copy
login_manager.login_message = 'Musisz być zalogowany aby otrzymać dostęp do tej strony!'
login_manager.login_message_category = 'info' #copy

from appData import routes