from flask_wtf import FlaskForm
import email_validator
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, BooleanField, SelectMultipleField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), Length(max=15)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    city = StringField('City',validators=[DataRequired()])
    state = StringField('State',validators=[DataRequired()])

class EditUserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), Length(max=15)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
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
    moon_phase = SelectField('Moon Phase',  choices=[('', 'None'),('0.97, 1.00', 'Full Moon'),('0.00, 0.03', 'New Moon'),('0.04, 0.39', 'Crescent Moon'),('0.40, 0.60', 'Quarter Moon'),('0.61, 0.96', 'Gibbous Moon')])
    weather_condition = SelectMultipleField('Weather Condition',  choices=[('', 'None'),('Clear', 'Clear Sky'), ('Clouds', 'Cloudy'), ('Snow', 'Snowy'), ('Rain', 'Rainy'), ('Drizzle', 'Drizzle'), ('Thunderstorm', 'Thunderstorm')])
    uvi = SelectField('UVI',  choices=[('', 'None'),('0.0,3.0', 'Low(0-2)'),('3.0,6.0', 'Medium(3-5)'),('6.0,8.0', 'High(6-8)'),('8.0,11.0', 'Very High(9-11)'),('11.0,15.0', 'Extreme(11+)')])


class MakePostForm(FlaskForm):
    """make post form"""

    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description')
    # public = BooleanField('Make public')