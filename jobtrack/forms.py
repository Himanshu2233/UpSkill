from datetime import date
from urllib.parse import urlsplit

from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from .models import STATUSES


def strip_text(value):
    return value.strip() if value else value


class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email(), Length(max=254)], filters=[strip_text])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Log in')


class RegisterForm(LoginForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create account')


class ApplicationForm(FlaskForm):
    company = StringField('Company', validators=[DataRequired(), Length(max=120)], filters=[strip_text])
    title = StringField('Job title', validators=[DataRequired(), Length(max=160)], filters=[strip_text])
    posting_url = StringField('Posting URL (optional)', validators=[Optional(), Length(max=2048)], filters=[strip_text])
    application_date = DateField('Application date', default=date.today, validators=[DataRequired()])
    deadline = DateField('Deadline (optional)', validators=[Optional()])
    status = SelectField('Status', choices=[(s, s) for s in STATUSES], validators=[DataRequired()])
    notes = TextAreaField('Notes (optional)', validators=[Length(max=10000)], filters=[strip_text])
    submit = SubmitField('Save application')

    def validate_posting_url(self, field):
        try:
            parsed = urlsplit(field.data)
            if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname or any(c.isspace() for c in field.data):
                raise ValueError()
            parsed.port
        except ValueError:
            raise ValidationError('Enter a valid http:// or https:// URL.')


class ActionForm(FlaskForm):
    submit = SubmitField('Confirm')
