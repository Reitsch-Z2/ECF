import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DecimalField, DateField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Length
from app.models import User
from app.utils.helpers import json_loader


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    currencies = json_loader(True, 'settings', 'general', 'currencies')
    username = StringField('Username', validators=[
        Length(min=6, message='Username must be at least 6 characters')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password2 = PasswordField('Repeat the password', validators=[DataRequired(), EqualTo('password')])
    currency = SelectField('Base currency', choices=currencies, validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username (self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email (self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError('Email already exists.')


class ItemForm(FlaskForm):
    item = StringField('Item', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    currency = SelectField('Currency', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    date = DateField('Time', default=datetime.date.today(), format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # Prevents the user from making entries for the dates in the future - mostly because the currency exchange rates
    # data does not exist yet and the conversions cannot be made if the currency for the entry is not the default one
    def validate_date (self, date):
        if date.data.strftime('%Y-%m-%d') > datetime.date.today().strftime('%Y-%m-%d'):
            raise ValidationError('The date cannot be in the future')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat the password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request password reset')


class EditUserPersonalForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class EditUserPasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[DataRequired()])
    password2 = PasswordField('Repeat the password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def __init__(self, username, *args, **kwargs):  # Used to pass the current user's username as the argument for
        super().__init__(*args, **kwargs)           # identification in order to validate the old/current password
        self.username=username

    def validate_old_password (self, old_password):
        user = User.query.filter_by(username=self.username).first()
        if user.check_password(old_password.data) != True:
            raise ValidationError('The current password is incorrect.')


class EditUserSettingsForm(FlaskForm):
    currency = SelectField('Currency', validators=[DataRequired()])
    save_query = SelectField('Remember queries', validators=[DataRequired()])
    submit = SubmitField('Submit')

