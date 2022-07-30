from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField, DecimalField, DateField #TODO any superfluous?
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email        #TODO any superfluous?
from app.utils.helpers import json_loader
from app.models import User

from app import login
from flask_login import current_user
import datetime



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat the password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username (self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email (self,email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Email already exists.')

class ItemForm(FlaskForm):

    currencies = json_loader(True, "settings", "general", "currencies")

    item = StringField('Item', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])              #TODO is it?
    currency = SelectField('Currency', choices=currencies, validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])         #TODO is it?
    date = DateField('Time', default=datetime.date.today(), format='%Y-%m-%d', validators=[DataRequired()])         #TODO format is acting fishy
    submit = SubmitField('Submit')

    #TODO - surely some custom validators here