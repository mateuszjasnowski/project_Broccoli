from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
#dlugie importy ->
#from wtforms import (
#   StringField,
#   PasswordField,
#   SubmitField,
#   BooleanField,
#   TextAreaField
#)

from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from appData.models import User


class RegistrationForm(FlaskForm):#nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    login = StringField('login', validators=[DataRequired(), Length(min=1,max=30)])# spacja po przecinku
    userFirstName = StringField('userFirstName', validators=[Length(max=30)])
    userLastName = StringField('userLastName', validators=[Length(max=30)])
    email = StringField('email', validators=[DataRequired(), Length(min=4,max=120)])# spacja po przecinku
    password = PasswordField('Password', validators=[DataRequired()])


    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    # pierdola ale raczej tak sie formatuje
    # username = StringField(
    #   'Username',
    #   validators = [
    #       DataRequired(),
    #       Length(min=2, max=20)
    #   ]
    # )                           
    email = StringField('Email',
                        validators=[DataRequired(), Length(min=4, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    #nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    #nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm): #nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm): #nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    #nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    #nie znalazlem uzycia - jak nie ma to do wywalenia lub do uzycia ;D
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
#brak pustej lini na koncu pliku, odpal sobie jakiegos lintera i zobacz co Ci poznajduje + poczytaj o PEP8