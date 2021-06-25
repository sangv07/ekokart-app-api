import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse  # to generate API's url

from rest_framework.test import APIClient
from rest_framework import status


# app/user/urls.py =>> name='create', name='token'
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# creating Public and Private API so that Public API => unauthenticated so that it just anyone from internet can make a request
# eg. create_user => we can make user from public because we don't have authentication setup yet.
# eg of Private API => modifying USER, Delete User, Change Password (these needs authentication)
class PublicUserApiTests(TestCase):
    """Test the user API (Public)"""

    def setUp(self):
        # https://www.django-rest-framework.org/api-guide/testing/
        # The APIClient class supports the same request interface as Django's standard Client class.
        # This means that the standard .get(), .post(), .put(), .patch(), .delete(), .head() and .options() methods are all available. For example:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        # payload = {} is the objects that you pass to the API when you make the request
        payload = {
            'email': os.environ.get('USER_EMAIL'),
            'password': os.environ.get('USER_PASS'),
            'username': os.environ.get('USER_NAME'),

        }
        # res = self.client.post('/notes/', {'title': 'new idea'}, format='json')
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # testing if object is actually created
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_exists(self):
        """Test creatings user that already exists fails"""
        payload = {
            'email': os.environ.get('USER_EMAIL'),
            'password': os.environ.get('USER_PASS'),
            'username': os.environ.get('USER_NAME'),
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 Characters"""
        payload = {
            'email': os.environ.get('USER_EMAIL'),
            'password': 'PW',
            'username': os.environ.get('USER_NAME'),

        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test taht a token is created for the user"""
        payload = {
            'email': os.environ.get('USER_EMAIL'),
            'password': os.environ.get('USER_PASS'),
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email=os.environ.get('USER_EMAIL'), password=os.environ.get('USER_PASS'))
        payload = {'email': os.environ.get('USER_EMAIL'),
                   'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not cerated if user doesn't exist"""
        payload = {'email': os.environ.get('USER_EMAIL'),
                   'password': os.environ.get('USER_PASS')
                   }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one',
                                           'password': ''}
                               )
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email=os.environ.get('USER_EMAIL'),
            password=os.environ.get('USER_PASS'),
            username=os.environ.get('USER_NAME'),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            # referencing from method setUp()
            'username': self.user.username,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on the me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'username': os.environ.get('NEW_USER_NAME'), 'password': os.environ.get('NEW_USER_PASS')}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
