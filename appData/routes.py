from flask import render_template, url_for, flash, redirect, request
from appData import app

pageList = [
        {'name': 'start', 'href': 'home'},
        {'name': 'o projekcie', 'href': 'about'},
        {'name': 'admin', 'href': 'admin'}
    ]


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', title='Start', pageList=pageList)


@app.route('/login')
def login():
    return render_template('login.html', title='Logowanie', pageList=pageList)


@app.route('/register')
def register():
    return render_template('register.html', title='Rejestracja', pageList=pageList)
def register(message):
    return render_template('register.html', title='Rejestracja', pageList=pageList, message=message)


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
def terms(*args):
    print('kurwaaa')
    return redirect(url_for('register',title=args)) #TODO
