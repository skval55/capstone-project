import os
import json
from unittest import TestCase

from models import db, User, Activity, Post

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///climate-connect-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True


class UserViewTestCaseLoggedIn(TestCase):
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

    def test_homepage(self):
        """test user user search up"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

              
            resp = c.get("/homepage")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<a class="text-gray-500 hover:underline hover:text-gray-300" href="/add-activity">Add an activity</a>', html)
    
    def test_add_activity(self):
        """test user user search up"""


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

              
            resp = c.get("/add-activity")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h3 class=" text-3xl font-bold text-gray-100">Create Activity</h3>', html)
    
    def test_add_activity_post(self):
        """test user user search up"""
        

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            
            data = {
                'name': 'test activity',
                'min_temp': '0',
                'max_temp': '99',
                'sun': True,
                'show_moon': True,
                'moon_phase':'0.97, 1.00',
                'weather_condition': 'Clear',
                'uvi': '0.0,3.0'
            }
            response = c.post('/add-activity', data=data, follow_redirects=True)

            # check that the response is successful
            self.assertEqual(response.status_code, 200)

            # check that the activity was added to the database
            activity = Activity.query.filter_by(name='test activity').first()
            self.assertIsNotNone(activity)
    
    def test_post_activity_page(self):
        """test user user search up"""

       
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            day_data = {"city":"St. George","state":"Utah","timeOfDay":["morn"],"dayIndex":"0","temp":{"day":74.68,"eve":78.08,"max":78.35,"min":58.68,"morn":58.68,"night":67.98},"weather":{"description":"clear sky","icon":"01d","id":800,"main":"Clear"},"rain":0,"moonPhase":40,"showMoon":"hidden","uvi":8.15,"icon":"01d","theme":"light","times":{"dt":"Tuesday, 5/2/2023","sunrise":"6:38:47 AM","sunset":"8:23:43 PM","moonrise":"5:34:00 PM","moonset":"5:12:00 AM"},"activity":"Running","activityId":"3"}
              
            data = {'day-data': json.dumps(day_data)}
            response = c.post('/make-post', data=data, follow_redirects=True)
            html = response.get_data(as_text=True)

             # Check that the response is successful
            self.assertEqual(response.status_code, 200)
            self.assertIn('<div class="text-3xl font-bold text-gray-100 text-center">Create Post</div>', html)
    
    def test_post_post(self):
        """Test posting a new post"""
        print('postpost')
        with self.client as c:
            # Log in the test user
            day_data = day_data = {"city":"St. George","state":"Utah","timeOfDay":["morn"],"dayIndex":"0","temp":{"day":74.68,"eve":78.08,"max":78.35,"min":58.68,"morn":58.68,"night":67.98},"weather":{"description":"clear sky","icon":"01d","id":800,"main":"Clear"},"rain":0,"moonPhase":40,"showMoon":"hidden","uvi":8.15,"icon":"01d","theme":"light","times":{"dt":"Tuesday, 5/2/2023","sunrise":"6:38:47 AM","sunset":"8:23:43 PM","moonrise":"5:34:00 PM","moonset":"5:12:00 AM"},"activity":"Running","activityId":self.testactivity.id}
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                sess['day_data'] = day_data
    

            # Set up form data
            form_data = {
                'title': 'Test post',
                'description': 'This is a test post',
            }

            # Send a POST request to the route with the form data
            response = c.post('/make-post/post', data=form_data, follow_redirects=True)
            html = response.get_data(as_text=True)

            # Check that the response is successful
            self.assertEqual(response.status_code, 200)
            self.assertIn('<h3 class="text-2xl capitalize">Test post</h3>', html)

            # Check that the post was added to the database
            post = Post.query.filter_by(title='Test post').first()
            self.assertIsNotNone(post)
            self.assertEqual(post.user_Id, self.testuser.id)
            self.assertEqual(post.activity_Id, day_data['activityId'])
            self.assertEqual(post.description, 'This is a test post')


    def test_edit_activity(self):
        """Test to see if you can edit post"""
        print('postpost44444444')
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

              
            response = c.get(f"/edit-activity/{self.testactivity.id}")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('required type="text" value="test activity">', html)

    
    def test_edit_activity_post(self):
        """Test to see if you can edit post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            data = {
                'name': 'edited',
                'min_temp': '0',
                'max_temp': '99',
                'sun': True,
                'show_moon': True,
                'moon_phase':'0.97, 1.00',
                'weather_condition': 'Clear',
                'uvi': '0.0,3.0'
            }
              
            response = c.post(f"/edit-activity/{self.testactivity.id}", data=data, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h3 class="text-center text-xl font-bold text-gray-100 capitalize">edited</h3>', html)

    def test_edit_user(self):
        """Test to see if you can edit post"""
        print('postpost44444444')
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

              
            response = c.get(f"/users/edit")
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h3 class=" text-3xl font-bold text-gray-100 text-center">Edit User</h3>', html)

    
    def test_edit_user(self):
        """Test to see if you can edit post"""
        print('postpost44444444')
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            data = {'username':"edited",
                                    'first_name':'edited',
                                    'last_name':'user',
                                    'email':"test@test.com",
                                    'image_url':None,
                                    'city':'ivins',
                                    'state':'utah',
            }
              
            response = c.post(f"/users/edit", data=data, follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h3 class="text-3xl capitalize ">edited</h3>', html)