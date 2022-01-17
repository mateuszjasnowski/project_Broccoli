from datetime import datetime
from appData import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader #copy
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), unique=True, nullable=False)
    firstname = db.Column(db.String(30))
    lastname = db.Column(db.String(30))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(90), nullable=False)
    role = db.Column(db.String(30), default='User')
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.login}', '{self.firstname}', '{self.lastname}', '{self.email}', '{self.role}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manufacture = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    manufacture_year = db.Column(db.String(4))
    photo = db.Column(db.String(30), nullable=False, default='defaultCar.jpg')
    description = db.Column(db.Text)
    price = db.Column(db.Integer(), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #status = db.Column(db.String(10), default='published') #TODO
    #postVisitCount = db.Column(db.Integer(), nullable=False, default=0) #TODO not big piority

    def __repr__(self):
        return f"Post('{self.id}','{self.author}','{self.manufacture}','{self.model}','{self.manufacture_year}','{self.photo}','{self.description}','{self.price}','{self.date_posted}')"