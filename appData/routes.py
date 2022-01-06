from flask import render_template, url_for, flash, redirect
from appData import app

pageList = ['home', 'about', 'admin']


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', title='Home', pageList=pageList)


@app.route('/login')
def login():
    return 'Login'


@app.route('/register')
def register():
    return 'Register'


@app.route('/about')
def about():
    return 'Hi'


@app.route('/admin')
def admin():
    return 'Hi'
