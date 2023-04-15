import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Activity, Going, Likes, Follows
from forms import UserAddForm, LoginForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///climate_connect'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

db.drop_all()
db.create_all()

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
                location=form1.location.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Username already taken")
            return redirect('/', form1=form1, form2=form2)
        
        return redirect("/homepage")

    if form2.validate_on_submit():
        try:
            user = User.authenticate(
                username=form2.username.data,
                password=form2.password.data
            )
        except IntegrityError:
            flash("Incorrect Username or Password")
            return render_template('/', form1=form1, form2=form2)

        return redirect("/homepage")

    return render_template('base.html', form1=form1, form2=form2)


@app.route('/homepage')
def homepage():

    return '<h1>ya don it!</h1>'
