import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Activity, Going, Likes, Follows, Post
from forms import UserAddForm, LoginForm, AddActivityForm, MakePostForm, EditUserForm
import requests
import json


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///climate_connect'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)


# with app.app_context():
#     connect_db(app)

connect_db(app)

# Custom Jinja2 filter to deserialize JSON strings
@app.template_filter('json_loads')
def json_loads_filter(value):
    return json.loads(value)

##########################################################
# global variables
CURR_USER_KEY = "curr_user"


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
    if CURR_USER_KEY in session:
        return redirect('/homepage')

    form1 = UserAddForm()
    form2 = LoginForm()

    if form1.validate_on_submit():
        response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={form1.city.data},{form1.state.data},USA&limit=1&appid=296cd6aaf1d515387c708caa99264128' )
        data = json.loads(response.text)
        lat = data[0]['lat']
        lon = data[0]['lon']

 
        try:
            user = User.signup(
                username=form1.username.data,
                first_name=form1.first_name.data,
                last_name=form1.last_name.data,
                password=form1.password.data,
                email=form1.email.data,
                image_url=form1.image_url.data or User.image_url.default.arg,
                city=form1.city.data,
                state=form1.state.data,
                lat= lat,
                lon=lon
            )
            db.session.commit()

        except IntegrityError:
            flash("Username or email already taken")
            return render_template('landing.html', form1=form1, form2=form2)
        
        do_login(user)
        return redirect("/homepage")

    if form2.validate_on_submit():
    
        user = User.authenticate(
            username=form2.username.data,
            password=form2.password.data
            )
        if user:
            do_login(user)
            return redirect("/homepage")

        
        flash("Incorrect Username or Password")
        return render_template('landing.html', form1=form1, form2=form2)

        
    return render_template('landing.html', form1=form1, form2=form2)


@app.route('/logout')
def logout():
    """logout user"""

    do_logout()
    return redirect('/')


###############################################################
# main page for user with user posts

@app.route('/homepage')
def show_posts():

    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user
    posts = Post.query.filter(Post.user_Id == user.id)

    return render_template('posts/posts.html', posts=posts, user=user)

@app.route('/explore')
def show_all_posts():

    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user
    posts = Post.query.all()

    return render_template('posts/all-posts.html', posts=posts, user=user)


##############################################################
# user routes


@app.route('/users/edit', methods=['POST','GET'])
def edit_user():
    """edit user info"""
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user
    form = EditUserForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.image_url = form.image_url.data
        user.city = form.city.data
        user.state = form.state.data
        db.session.commit()

        return redirect('/homepage')

    return render_template('user/edit-user.html', user = user, form = form)

@app.route('/users/delete/sure')
def permission_to_delete():
    """page to be sure ro delete profile"""
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user
    return render_template('user/sure-delete.html', user=user)


@app.route('/users/delete', methods=['POST'])
def delete_user():
    """delete user"""
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')

    user = g.user
    db.session.delete(user)
    db.session.commit()

    do_logout()

    return redirect('/')


##############################################################
# activity routes

@app.route('/add-activity', methods=['POST', 'GET'])
def add_activity():
    """show add activity form"""
    print('add_activity function called')
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')

    user = g.user

    form = AddActivityForm()


    if form.validate_on_submit():
        print('###################yay$###################')
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
        return redirect('/homepage')

    print('form not submitted')
    return render_template('activities/add-activity.html', form = form, user = user)

@app.route('/edit-activity/<int:activity_id>', methods=['POST', 'GET'])
def editActivity(activity_id):
    """edit activity"""
    print('ramnnnnnnn')
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user
    activity = Activity.query.get_or_404(activity_id)
    form = AddActivityForm()

    if form.validate_on_submit():
        data = dict(filter(filter_form, form.data.items()))
        activity.name = data.get('name')
        activity.max_temp = data.get('min_temp', None)
        activity.min_temp = data.get('max_temp', None)
        activity.sun = data.get('sun', None)
        activity.show_moon = data.get('show_moon', None)
        activity.moon_phase = data.get('moon_phase', None)
        activity.weather_condition = data.get('weather_condition', None)
        activity.uvi = data.get('uvi', None)
        db.session.commit()

        return redirect('/search-activity')

    
    return render_template('activities/edit-activity.html', form = form, user = user, activity=activity)

@app.route('/delete-activity/<int:activity_id>')
def delete_activity(activity_id):
    """delete post"""
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()

    return redirect('/search-activity')


def filter_form(pair):
    unwanted_key = 'csrf_token'
    unwanted_values = ['', None, [''], {}]
    key, value = pair
    if key == unwanted_key or value in unwanted_values:
        return False
    else:
        return True

@app.route('/search-activity')
def search_activity_page():
    """show activities so they can choose to search api for one"""

    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user

    activities = Activity.query.filter(Activity.user_Id == user.id)

    return render_template('activities/search-activity.html', user = user, activities=activities)


##############################################################
# post routes


@app.route('/make-post' , methods=['POST'])
def make_post():
    """show make post form and post post to main page"""

    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    
    dayStr = request.form['day-data']
    print(dayStr)
    day = json.loads(dayStr)
    session["day_data"] = day

    form = MakePostForm()
    user = g.user

    return render_template('posts/make-post.html', form=form, user=user, day=day )


@app.route('/make-post/post' , methods=['POST'])
def post_post():

    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    user = g.user
    day = session['day_data']
    print(day)
    print('#####################################')
    form = MakePostForm()

    if form.validate_on_submit():
        post = Post(
            user_Id = user.id,
            activity_Id = day['activityId'],
            title = form.data['title'],
            description = form.data['description'],
            weather_data = json.dumps(day)
            # public = form.data['public']
        )
        db.session.add(post)
        db.session.commit()
        return redirect('/homepage')


@app.route('/delete-post/<int:post_id>')
def delete_post(post_id):
    """delete post"""
    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect('/homepage')

@app.route('/edit-post/<int:post_id>', methods=['POST', "GET"])
def edit_post(post_id):

    if CURR_USER_KEY not in session:
        flash('not authorized', 'top')
        return redirect('/')

    user = g.user
    form = MakePostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        # post.public = form.public.data
        db.session.commit()

        return redirect('/homepage')
    

    return render_template('posts/edit-post.html', user= user, form=form, post=post)

def serialize_activity(activity):
    """make activity serialized for json"""
    parameters = {}



    return {
        'name': activity.name,
        'min_temp': activity.min_temp, 
        'max_temp': activity.max_temp,
        'sun': activity.sun ,
        'show_moon': activity.show_moon,
        'moon_phase': activity.moon_phase,
        'weather_condition': activity.weather_condition,
        'uvi': activity.uvi
    }


##############################################################
# API routes


@app.route('/api/search-activity/<int:activity_id>')
def search_activity(activity_id):
    """show activities so they can choose to search api for one"""
    user = g.user
    activity = Activity.query.get_or_404(activity_id)
    serialized_activity = serialize_activity( activity)

    return jsonify(search = {'activity':serialized_activity})

@app.route('/api/get-day-data')
def search_day_data():
    """show activities so they can choose to search api for one"""

    user = g.user
    response = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={user.lat}&lon={user.lon}&units=imperial&exclude=hourly,minutely,current&appid=296cd6aaf1d515387c708caa99264128' )
    days = json.loads(response.text)

    return jsonify(search = {'days':days, 'city':user.city, 'state':user.state})
    





