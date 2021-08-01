from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

from app.models import User

'''
# Tutorial of flask-wtf
# https: // flask - wtf.readthedocs.io / en / 0.15.x / quickstart /
# Tutorial of wtforms
# https: // flask.palletsprojects.com/en/2.0.x/patterns/wtforms/#
'''


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    # recaptcha = RecaptchaField()
    submit = SubmitField('Sign up')

    # check username duplicated or not
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username has already been taken')

    # check email duplicated or not
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email has already been taken')


class SignInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class ResetPasswordRequestForm(FlaskForm): # for forgot_password.html
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email not exists')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ContactUsForm(FlaskForm):
    text = TextAreaField('Say something ...', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Post')


class UploadAvatarForm(FlaskForm):
    avatar = FileField('avatar', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only!!')
    ])
    submit = SubmitField('Upload')

