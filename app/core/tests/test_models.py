from django.test import TestCase
from django.contrib.auth import get_user_model

# from core.calc import add, subtract


# Django searches for any Python Module starting with "test".
#   This is why you can store your tests in "tests.py" or "tests/test_something.py"
class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test Creating a new user with an email is successful"""
        email = 'test@appdev.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a  new user is normalized"""
        email = 'test@APPDEV.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):  # core/models/UserManager.create_user() if not email:
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating new super_user"""
        superuser = get_user_model().objects.create_superuser(
            first_name='sangv',
            last_name='stha',
            username='sangv07',
            email = 'test@appdev.com',
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
