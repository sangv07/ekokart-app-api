import uuid
import os

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.conf import settings


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('uploads/recipe/', filename)

# Create your models here.
class UserManager(BaseUserManager):

    # Creating new user and save in DB
    def create_user(self, email, password=None, **extra_fields):
        """ **extra_fields is used for dynamic other_fields
           Custom_User_Model_Manger where email is the unique identifiers for authentication instead of username.
        """
        if not email:
            raise ValueError("User must have E-mail Address.")

        user = self.model(
            email=self.normalize_email(email),  # Normalizing = (everything after the "@") is lowercase
            **extra_fields,
        )
        # set_password will encrypt(hash) password with that it would not be access or modified.
        user.set_password(password)
        user.save(using=self._db)  # using=self._db => is required for supporting multiple database

        return user

    def create_superuser(self, first_name, last_name, username, email, password=None):
        """Custom_create_super_user_Model"""
        user = self.create_user(
            email       = self.normalize_email(email),
            first_name  = first_name,
            last_name   = last_name,
            username    = username,
            password    =password
        )
        user.is_active     = True
        user.is_superuser  = True
        user.is_admin      = True
        user.is_staff      = True

        user.save(using=self._db)

        return user


# PermissionMixin add fields that are specific for objects that have permissions, like is_superuser, groups, and user_permissions
# It also provides a set of utility methods to check if the model with this mixin has a given permission (for example with has_perm)
class UserAccount(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    first_name  = models.CharField(max_length=100, verbose_name='first_name')
    last_name   = models.CharField(max_length=255, verbose_name='last_name')
    username    = models.CharField(max_length=50)
    email       = models.EmailField(max_length=255, unique=True, blank=False)
    phone       = models.CharField(max_length=10)

    # Required Fields
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='date_joined')
    is_active   = models.BooleanField(default=True, verbose_name='is_active')
    is_admin    = models.BooleanField(default=False, verbose_name='is_admin')
    is_staff    = models.BooleanField(default=False, verbose_name='is_staff')
    # this will pop when running "python manage.py createsuperuser"
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'User_Account'

    objects = UserManager()

    # This just means that when we return the account object inside the template. So this should return the email address.
    def __str__(self):
        return self.email


# creating class tags() because AttributeError: module 'core.models' has no attribute 'Tag'
class Tag(models.Model):
    """Tag to be used for a recipe"""
    print('*****Tag_Model*****')

    # Id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    tag_name = models.CharField(max_length=255)
    useraccount = models.ForeignKey(
        settings.AUTH_USER_MODEL,   # Note that Django suggests getting the User from the settings for relationship definitions
        on_delete=models.CASCADE,

    )

    # String Representation
    def __str__(self):
        return self.tag_name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    print('*****Ingredient_Model*****')

    ing_name = models.CharField(max_length=255, verbose_name='ing_name')
    useraccount = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.ing_name


class Recipe(models.Model):
    """Recipe to be used in the Recipe"""
    print('*****Recipe_Model*****')

    title       = models.CharField(max_length=255)
    time_minutes= models.IntegerField()
    price       = models.DecimalField(max_digits=3, decimal_places=2)
    link        = models.CharField(max_length=255, blank=True)

    # ('Ingredient') if we don't user '' in string then Ingredients class need to be top of this class.
    # but if we use '' in string then it doesn't matter the order or classes.
    ingredient_fk = models.ManyToManyField('Ingredient')  # relational model with Ingredient class
    tag_fk        = models.ManyToManyField('Tag')  # relational model with Tag class

    useraccount = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)  # added image field to handle Images (veiws, serializer)

    # String Representation
    def __str__(self):
        return self.title
