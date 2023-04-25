
from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

now = datetime.utcnow

class Follows(db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class Likes(db.Model):
    """Connection of a user to liked activities"""

    __tablename__ = 'likes'

    activity_Id = db.Column(
        db.Integer,
        db.ForeignKey('activities.id', ondelete="cascade"),
        primary_key=True,
    )
    
    user_Id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class Going(db.Model):
    """Connection of a user to liked activities"""

    __tablename__ = 'going'

    activity_Id = db.Column(
        db.Integer,
        db.ForeignKey('activities.id', ondelete="cascade"),
        primary_key=True,
    )
    
    user_Id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class User(db.Model):
    """user model with connection to likes, activities, follows"""

    __tablename__ = "users"


    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.Text,
        nullable=False
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/user-icon.png"
    )

    city = db.Column(
        db.Text
    )

    state = db.Column(
        db.Text
    )

    lat = db.Column(db.Float)

    lon = db.Column(db.Float)

    password = db.Column(
        db.Text,
        nullable=False
    )

    activities = db.relationship('Activity', cascade="all, delete-orphan")

    likes = db.relationship(
        'Activity',
        secondary="likes"
    )

    going = db.relationship(
        'Activity',
        secondary="going"
    )

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )



    @classmethod
    def signup(cls, username,first_name, last_name, city, state, email, password, image_url, lat, lon):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            city=city,
            state=state,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            lat=lat,
            lon=lon
        )

        db.session.add(user)
        return user

    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Activity(db.Model):
    """activities model"""

    __tablename__ = "activities"

    id = db.Column(db.Integer,
        primary_key=True)

    user_Id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"))

    name = db.Column(db.Text, nullable=False)

    min_temp = db.Column(db.Integer)
    
    max_temp = db.Column(db.Integer)

    sun = db.Column(db.Boolean)

    show_moon = db.Column(db.Boolean)

    moon_phase = db.Column(db.Text)

    weather_condition = db.Column(db.Text)

    uvi = db.Column(db.Text)


class Post(db.Model):
    """posts model"""

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
        primary_key=True)

    user_Id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"))
 
    activity_Id = db.Column(
        db.Integer,
        db.ForeignKey('activities.id', ondelete="cascade"))

    title = db.Column(db.Text, nullable=False)

    description = db.Column(db.Text)

    weather_data = db.Column(db.Text)

    public = db.Column(db.Boolean)

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
    app.app_context().push()

