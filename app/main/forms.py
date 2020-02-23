from flask_wtf import FlaskForm
from flask_login import current_user
from werkzeug.security import generate_password_hash
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    IntegerField, SelectField, FileField, DateTimeField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from app.models import User
import string

FALSE_VALUES = {False, 'false', 'n', ''}


'''
Form for login
'''
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')  # text that goes in the button


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')  # text that goes in the button


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username Taken! Please use a different username...')
