from datetime import datetime #models
from flask import render_template, url_for, flash, redirect, request
from appData import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required #copy



#db classess
class User(db.Model):
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
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manufacture = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    manufacture_year = db.Column(db.String(4))
    photo = db.Column(db.String(30), nullable=False, default='defaultCar.jpg')
    description = db.Column(db.Text),
    price = db.Column(db.Integer(), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.id}','{self.author}','{self.manufacture}','{self.model}','{self.manufacture_year}','{self.photo}','{self.description}','{self.price}','{self.date_posted}')"




posts = [
    {
        'id': 1,
        'author': "Jan Kowalski",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
    {
        'id': 2,
        'author': "roman",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
        {
        'id': 1,
        'author': "Jan Kowalski",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
    {
        'id': 2,
        'author': "roman",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
        {
        'id': 1,
        'author': "Jan Kowalski",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
    {
        'id': 1,
        'author': "Jan Kowalski",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
    {
        'id': 2,
        'author': "roman",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
        {
        'id': 1,
        'author': "Jan Kowalski",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
    {
        'id': 2,
        'author': "roman",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
        {
        'id': 1,
        'author': "Jan Kowalski",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    },
    {
        'id': 2,
        'author': "roman",
        'manufacture': 'Benfactor',
        'model': 'Shafter',
        'manufacture_year': '2012',
        'photo': 'shafter.jfif',
        'description': 'This is a car from GTA V',
        'price': 12000,
        'date_posted': 'April 21, 2018'
    }
]



#side routes
@app.route('/')
@app.route('/home') #TODO
def home():
    return render_template('index.html', title='Start', posts = posts)


@app.route('/login')
def login():
    return render_template('login.html', title='Logowanie')


@app.route('/register')
def register():
    return render_template('register.html', title='Rejestracja')
def register(message):
    return render_template('register.html', title='Rejestracja', message=message)


@app.route('/register_proceed', methods=["POST"])
def register_proceed():
    formData = request.form.get('login')
    if formData == '123':
        return redirect(url_for('register', message='Email already used'))
    else:
        return formData


@app.route('/about')
def about():
    return 'Hi' #TODO


@app.route('/admin')
def admin():
    return 'Hi' #TODO


@app.route('/terms')
def terms():
    return 'Terms' #TODO
