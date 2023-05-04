"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Activity, Post


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///climate-connect-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.drop_all()
db.create_all()

class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    first_name='test',
                                    last_name='user',
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    city='ivins',
                                    state='utah',
                                    lat='37.1685907',
                                    lon='-113.6794057'
                                    )

        db.session.commit()

        self.testuser2 = User.signup(username="testuser2",
                                    first_name='test2',
                                    last_name='user2',
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None,
                                    city='Salt lake city',
                                    state='utah',
                                    lat='37.104153',
                                    lon='37.104153'
                                    )

        db.session.commit()

        activity = Activity(
                user_Id = self.testuser.id,
                name = 'test activity',
                min_temp = '0',
                max_temp = '99',
                sun = True,
                show_moon = True,
                moon_phase = '0.97, 1.00',
                weather_condition = 'Clear',
                uvi = '0.0,3.0'
        )
        db.session.add(activity)
        db.session.commit()

        self.testactivity = activity

    def test_user_model(self):
        """does the user model work"""

        u = User(username="testusermodel",
                first_name='test',
                last_name='user',
                email="testmodel@test.com",
                password="testuser2",
                image_url=None,
                city='Salt lake city',
                state='utah',
                lat='37.104153',
                lon='37.104153'
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.activities), 0)
        self.assertEqual(len(u.posts), 0)
 
    def test_activity_model(self):
        """does the activity model work"""
        
        activity = Activity(
                user_Id = self.testuser.id,
                name = 'test activity',
                min_temp = '0',
                max_temp = '99',
                sun = True,
                show_moon = True,
                moon_phase = '0.97, 1.00',
                weather_condition = 'Clear',
                uvi = '0.0,3.0'
        )
        db.session.add(activity)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(activity.user_Id, self.testuser.id)
        self.assertEqual(activity.name, 'test activity')
   
    def test_post_model(self):
        """does the post model work"""
        
        post = Post(
                user_Id = self.testuser.id,
                activity_Id = self.testactivity.id,
                title = 'test activity',
                description = 'test description',
                weather_data = 'weather data',
                public = True
        )
        db.session.add(post)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(post.user_Id, self.testuser.id)
        self.assertEqual(post.title, 'test activity')

    def test_user_model_signup_unique(self):
        """test to see if signup has to be unique testing same user as in set up"""

        u = User.signup(username="testuser",
                                    first_name='test',
                                    last_name='user',
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    city='ivins',
                                    state='utah',
                                    lat='37.1685907',
                                    lon='-113.6794057'
                                    )
       
        try:
            db.session.add(u1)
            db.session.commit()
            self.assertTrue(False)
        except:
            self.assertTrue(True)


    def test_user_authenticate(self):
        """test if authenticator returns correct user"""

        u = User.authenticate(
            username="testuser",
            password="testuser"
        )

        self.assertEqual(u, self.testuser)

    def test_user_false_authenticate(self):
        """test if authenticator returns correct user"""

        u = User.authenticate(
            username="incorrecttestuser",
            password="testuser"
        )

        self.assertTrue(u != self.testuser)
    