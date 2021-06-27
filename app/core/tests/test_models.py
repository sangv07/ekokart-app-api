import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


# '''We're going to start by adding a unit test for getting the tag object as a string and then we're going to implement our model and
# then we're going to run our migrations to create the migration which would create the model in the database.'''
def sample_user(email=os.environ.get('USER_EMAIL'), password=os.environ.get('USER_PASS')):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


# Django searches for any Python Module starting with "test".
#   This is why you can store your tests in "tests.py" or "tests/test_something.py"
class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test Creating a new user with an email is successful"""
        email = os.environ.get('USER_EMAIL')
        password = os.environ.get('USER_PASS')
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a  new user is normalized"""
        email = os.environ.get('USER_EMAIL')
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):  # core/models/UserManager.create_user() if not email:
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating new super_user"""
        superuser = get_user_model().objects.create_superuser(
            first_name=os.environ.get('USER_FNAME'),
            last_name=os.environ.get('USER_LNAME'),
            username=os.environ.get('USER_NAME'),
            email = os.environ.get('USER_EMAIL'),
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    # import models from app/core/models/Tag()
    # '''when we convert our tag model to a string it gives us the name.
    #     So with Django models you can basically specify what field you  want to use when you convert the model to a string representation and we're
    #     going to set it to the name and we're really just using this test to verify that we can create a model that is called tag and that basically we have the tag option in our models.'''
    # create a simple test that creates a tag and verifies that it converts to the correct string representation.
    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            useraccount=sample_user(),
            tag_name='Non-Veg'
        )

        self.assertEqual(str(tag), tag.tag_name)

    # creating Ingredient Tags endpoint in that it allows us to create and list ingredients which we can later assign to recipes for the
    # purposes of filtering. We're going to start by adding our ingredient model
    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            useraccount=sample_user(),
            ing_name='Chicken'
        )

        self.assertEqual(str(ingredient), ingredient.ing_name)

    # to pass below test we have to create Recipe Class in core/models
    def test_recipe_str(self):
        """Test the recipe String Representation"""
        recipe = models.Recipe.objects.create(
            useraccount=sample_user(),
            title='Mo:Mo',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)

