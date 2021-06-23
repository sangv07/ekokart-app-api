from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse  # to generate API's url

from rest_framework.test import APIClient
from rest_framework import status


# app/user/urls.py =>> name='create', name='token'
CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# creating Public and Private API so that Public API => unauthenticated so that it just anyone from internet can make a request
# eg. create_user => we can make user from public because we don't have authentication setup yet.
# eg of Private API => modifying USER, Delete User, Change Password (these needs authentication)
class PublicUserApiTests(TestCase):
    """Test the user API (Public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        # payload is the objects that you pass to the API when you make the request
        payload = {
            'email': 'sangv@test.co',
            'password': 'pwd123',
            'username': 'sangv',

        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # testing if object is actually created
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)


    def test_user_exists(self):
        """Test creatings user that already exists fails"""
        payload = {
            'email': 'sangv@test.co',
            'password': 'pwd123',
            'username': 'sangv',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 Characters"""
        payload = {
            'email': 'sangv@test.co',
            'password': 'pw',
            'username': 'sangv',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test taht a token is created for the user"""
        payload = {'email': 'sangv@test.co',
                   'password': 'pwd123'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='sangv@test.co', password='pwd123')
        payload = {'email': 'sangv@test.co',
                   'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not cerated if user doesn't exist"""
        payload = {'email': 'sangv@test.co',
                   'password': 'pwd123'
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