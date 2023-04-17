from flask_wtf import FlaskForm
from wtforms import StringField, FileField, PasswordField, BooleanField, SubmitField, RadioField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

# these are the form classes that are utilized using the wtf forms module.
# This makes submissions much easier

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class Image1Form(FlaskForm):
    pic1 = FileField('Before Image', validators=[DataRequired()])
    bWeight = StringField('Before Weight', validators=[DataRequired()])
    bDate = StringField('Before Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Image2Form(FlaskForm):
    pic2 = FileField('After Image', validators=[DataRequired()])
    aWeight = StringField('After Weight', validators=[DataRequired()])
    aDate = StringField('After Date', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReflectionForm(FlaskForm):
    date = StringField('Title or Date', validators=[DataRequired()])
    reflection = TextAreaField('Reflection', validators=[DataRequired()])
    submit = SubmitField('Submit')

class workoutForm(FlaskForm):
    date = StringField('Title or Date', validators=[DataRequired()])
    bodypart = TextAreaField('Body Part Hit', validators=[DataRequired()])
    workout = TextAreaField('Workouts', validators=[DataRequired()])
    submit = SubmitField('Submit')

class BMRForm(FlaskForm):
    BMR = StringField('BMR', validators=[DataRequired()])
    submit = SubmitField('submit')

class CalForm(FlaskForm):
    cals = StringField('Calories', validators=[DataRequired()])
    date = StringField('Today\'s Date', validators=[DataRequired()])
    submit = SubmitField('submit')
