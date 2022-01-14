 #models
from flask import render_template, url_for, flash, redirect, request
from appData import app, db, bcrypt
#from appData.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from appData.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required #copy


'''posts = [
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
        'photo': 'defaultCar.jpg',
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
        'photo': 'defaultCar.jpg',
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
        'photo': 'defaultCar.jpg',
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
]'''

class BroccoliRegisterForm:
    def __init__(self, username, firstName, lastName, email, password):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password


    def isUsernameUsed(self):
        user = User.query.filter_by(login=self.username).first()
        if user:
            return False
        else:
            return True


    def isEmailUsed(self):
        email = User.query.filter_by(email=self.email).first()
        if email:
            return False
        else:
            return True



#side routes
@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
    return render_template('index.html', title='Start', posts = posts)


@app.route('/login')
def login():
    return render_template('login.html', title='Logowanie')


@app.route('/register', methods=["POST","GET"])
def register():
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    '''
    return render_template('register.html', title='Rejestracja')

@app.route('/register_proceed', methods=["POST"])
def register_proceed():
    formData = BroccoliRegisterForm(request.form.get('login'),request.form.get('userFirstName'),request.form.get('userLastName'),request.form.get('email'),request.form.get('password'))
    if formData.isUsernameUsed():
        if formData.isEmailUsed():
            hashed_password = bcrypt.generate_password_hash(formData.password).decode('utf-8')
            user = User(login=formData.username, firstname=formData.firstName, lastname=formData.lastName, email=formData.email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        else:
            flash('Istnieje już konto z podanym adresem email.','danger')
            return redirect(url_for('login'))
    else:
        flash('Użytkownik o podanym loginie już istnieje. Wybierz inny login.','danger')
        return redirect(url_for('register'))


@app.route('/about')
def about():
    return 'Hi' #TODO


@app.route('/admin')
def admin():
    return 'Hi' #TODO


@app.route('/terms')
def terms():
    return 'Terms' #TODO


@app.route('/new_post')
def new_post():
    return 'Soon TM' #TODO