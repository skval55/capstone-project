import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Activity, Going, Likes, Follows
from forms import UserAddForm, LoginForm, AddActivityForm
import requests


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///climate_connect'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

CURR_USER_KEY = "curr_user"

connect_db(app)

# db.drop_all()
# db.create_all()

# ###############################################################
# login and logout routes and functions

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.route('/', methods=["GET", "POST"])
def login_page():
    """page to log in or sign up"""

    form1 = UserAddForm()
    form2 = LoginForm()

    if form1.validate_on_submit():
        try:
            user = User.signup(
                username=form1.username.data,
                first_name=form1.first_name.data,
                last_name=form1.last_name.data,
                password=form1.password.data,
                email=form1.email.data,
                image_url=form1.image_url.data or User.image_url.default.arg,
                city=form1.city.data,
                state=form1.state.data
            )
            print(user)
            print('*******************************')
            db.session.commit()

        except IntegrityError:
            flash("Username or email already taken")
            return render_template('base.html', form1=form1, form2=form2)
        
        do_login(user)
        return redirect("/homepage")

    if form2.validate_on_submit():
    
        user = User.authenticate(
            username=form2.username.data,
            password=form2.password.data
            )

        print(user)
        print("*****************************************")
        if user:
            do_login(user)
            return redirect("/homepage")

        
        flash("Incorrect Username or Password")
        return render_template('base.html', form1=form1, form2=form2)

        
    return render_template('base.html', form1=form1, form2=form2)


@app.route('/homepage')
def homepage():

    return render_template('activities/home.html')

@app.route('/logout')
def logout():
    """logout user"""

    do_logout()
    return redirect('/')


##############################################################
# other routes

@app.route('/users')
def show_profile():
    """show user profile"""
    user = g.user

    return render_template('activities/user.html', user = user)


@app.route('/add-activity', methods=['POST', 'GET'])
def add_activity():
    """show add activity form"""

    user = g.user

    form = AddActivityForm()
    print(form)
    for field in form:
        print(field)
        print('*********************************')
    print('*********************************')

    if form.validate_on_submit():
        data = dict(filter(filter_form, form.data.items()))
        activity = Activity(
            user_Id = session[CURR_USER_KEY],
            name = data.get('name'),
            min_temp = data.get('min_temp', None),
            max_temp = data.get('max_temp', None),
            sun = data.get('sun', None),
            show_moon = data.get('show_moon', None),
            moon_phase = data.get('moon_phase', None),
            weather_condition = data.get('weather_condition', None),
            uvi = data.get('uvi', None)
        )
        db.session.add(activity)
        db.session.commit()
        return redirect('/users')

    return render_template('activities/add-activity.html', form = form, user = user)

def filter_form(pair):
    unwanted_key = 'csrf_token'
    unwanted_values = ['', None, ['']]
    key, value = pair
    if key == unwanted_key or value in unwanted_values:
        return False
    else:
        return True

@app.route('/search-activity')
def search_activity_page():
    """show activities so they can choose to search api for one"""

    user = g.user
    response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={g.user.city},{g.user.state},USA&limit=1&appid=296cd6aaf1d515387c708caa99264128' )
    print(dir(response))
    print(response.text)
    print('**********************************************')
    print(response.json)
    print('**********************************************')
    print(response.content[1])
    print('**********************************************')
    print(dir(response.iter_content))
    print('**********************************************')

    activities = Activity.query.all()

    return render_template('activities/search-activity.html', user = user, activities=activities)
