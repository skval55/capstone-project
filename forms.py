from flask_wtf import FlaskForm
import email_validator
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    city = StringField('City',validators=[DataRequired()])
    state = StringField('State',validators=[DataRequired()])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class AddActivityForm(FlaskForm):
    """add activity form"""

    name = StringField('Name', validators=[DataRequired()])
    min_temp = IntegerField("Minimum Temperatue",  validators=[Optional()])
    max_temp = IntegerField("Maximum Temperatue",  validators=[Optional()])
    sun = BooleanField('Daylight',  validators=[Optional()])
    show_moon = BooleanField('Show Moon details',  validators=[Optional()])
    moon_phase = StringField('Moon Phase',  validators=[Optional()])
    weather_conditon = SelectMultipleField('Weather Condition',  choices=[('', 'None'),('Clear', 'Clear Sky'), ('Clouds', 'Cloudy'), ('Snow', 'Snowy'), ('Rain', 'Rainy'), ('Drizzle', 'Drizzle'), ('Thunderstorm', 'Thunderstorm')])
    uvi = IntegerField('UVI',  validators=[Optional()])
