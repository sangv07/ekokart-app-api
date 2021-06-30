import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse  # for generating the URLs

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# Assign a variable for our recipe URL to access the URL
RECIPES_URL = reverse('recipe:recipe-list')  # /api/recipe/recipe


# created to test image field and TestCase class RecipeImageUploadTests
def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

# to get Recipe by ID we need to create new Function() and provide 'Recipe_id'
def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])  # to GET detail by 'ID'


print('# sample are helper function for repeated objects needed for our test')
class HelperSample:

    # Instead of creating default value and **params we provide default value as function() parameters bcoz of only 2 fields required
    @staticmethod
    def sample_tag(user, tag_name='Non-Veg'):
        """Create and Return a Sample Tag for Recipe"""

        return Tag.objects.create(useraccount=user, tag_name=tag_name)

    @staticmethod
    def sample_ingredient(user, ing_name='Chicken'):
        """Create and Return a sample Ingredients for Recipe"""
        # default = {
        #     'ing_name': 'Chicken' #['chicken', 'cabbage', 'onion', 'dumpling_wrapper']
        # }
        # default.update(params)
        # return Ingredient.objects.create(useraccount=user, **default)
        return Ingredient.objects.create(useraccount=user, ing_name=ing_name)

    @staticmethod
    def sample_recipe(user, **params):
        """Create and return a sample recipe"""
        # creating default values for user and recipe but since 'user' will be pass by each TestCase
        default = {
            'title':'Mo:Mo',
            'time_minutes':10,
            'price': 7.00,
        }
        default.update(params)  # .update (its python Dict function it will update based on provided dict[key]) will to override default parameter if provided by tester through **params
        return Recipe.objects.create(useraccount=user, **default)


# Creating PublicRecipeTest
class PublicRecipeApiTests(TestCase):
    """Test the publicly available Recipe API"""

    # run function setUp() before every Test case under this Class
    def setUp(self):
        self.client = APIClient()

    def test_recipe_authentication(self):
        """Test that authentication required for retrieving recipe"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        # print(res.status_code)


class PrivateRecipeApiTest(TestCase):
    """Test the Authorized user tags API"""

    # run function setUp() before every Test case (for force_authentication to validate rest of the TestCAses)
    # create user_for_recipe using core/models.create_user() and use same user to force_authentication
    def setUp(self):
        self.client = APIClient()
        self.recipe_user = get_user_model().objects.create_user(
            os.environ.get('USER_EMAIL'),
            os.environ.get("USER_PASS")
        )

        self.client.force_authenticate(self.recipe_user)

    def test_retrieve_recipe(self):
        """Test retrieving a list of recipes"""
        HelperSample.sample_recipe(user=self.recipe_user)
        HelperSample.sample_recipe(user=self.recipe_user)

        # making request for URLs
        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)  # passing recipes into serializer

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user_only(self):
        """Test that Recipes return are for authenticated users only"""

        # creating User for Recipe in models
        self.recipe_user2 = get_user_model().objects.create_user(
            'otheruser@testapp.com',
            'testpass2'
        )

        # creating sample_recipe using authenticated user_1 and user_2
        HelperSample.sample_recipe(user=self.recipe_user2)
        HelperSample.sample_recipe(user=self.recipe_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(useraccount=self.recipe_user)

        # even we are only going to have one recipe for our specific user we still pass many equals true because even if there's just one object returned the list recipes API should always return the same data-type and that is a list so
        # if there's only one recipe then that list should just contain one item it shouldn't be just the object of the recipe it needs to be within a list
        # otherwise this makes the API inconsistent and you don't know what you're going to expect when you call the API.
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # length of data (there is only 1 data return)
        self.assertEqual(res.data, serializer.data)  # res.data is the data that was returned in the response and we expect that to equal the serializer data that we passed in

        # print(res.data)

    def test_view_recipe_detail(self):
        """Test Viewing a recipe detail"""

        # Creating Sample 'Recipe' in Database and we will created 'sample Tag' and 'sample Ingredients'
        # which eventually '.add' to Recipe's Tags and Ingredients Many-to-Many fields using Foreign_Key
        recipe = HelperSample.sample_recipe(user=self.recipe_user)
        recipe.tag_fk.add(HelperSample.sample_tag(user=self.recipe_user))
        recipe.ingredient_fk.add(HelperSample.sample_ingredient(user=self.recipe_user))

        url = detail_url(recipe.id)
        print('url', url)
        res = self.client.get(url)

        # Serializing return data to python data
        serializer = RecipeDetailSerializer(recipe)
        print(res.data, serializer.data)

        self.assertEqual(res.data, serializer.data)

    # Below 3 TestCases implemented Features for creating Recipes. (also added Perform_Created in Views/RecipeViewSet)
    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        print('=res.data["id"]',res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = HelperSample.sample_tag(user=self.recipe_user, tag_name='Vegan')
        tag2 = HelperSample.sample_tag(user=self.recipe_user, tag_name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tag_fk': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 9.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tag_fk.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = HelperSample.sample_ingredient(user=self.recipe_user, ing_name='Prawns')
        ingredient2 = HelperSample.sample_ingredient(user=self.recipe_user, ing_name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredient_fk': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredient_fk.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    # below 2 TestCase for updating Recipes
    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = HelperSample.sample_recipe(user=self.recipe_user)
        recipe.tag_fk.add(HelperSample.sample_tag(user=self.recipe_user))
        new_tag = HelperSample.sample_tag(user=self.recipe_user, tag_name='Non-Veg')

        payload = {'title': 'Chicken tikka', 'tag_fk': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tag_fk.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = HelperSample.sample_recipe(user=self.recipe_user)
        recipe.tag_fk.add(HelperSample.sample_tag(user=self.recipe_user))

        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tag_fk.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            os.environ.get('USER_EMAIL'),
            os.environ.get("USER_PASS")
        )
        self.client.force_authenticate(self.user)
        self.recipe = HelperSample.sample_recipe(user=self.user)

    # TearDown after each Test run
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)   # use this seek function to set the pointer back to the beginning of the file so then it's as if you've just opened it

            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Creating test for filtering Recipe
    def test_filter_recipes_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = HelperSample.sample_recipe(user=self.user, title='Thai vegetable curry')
        recipe2 = HelperSample.sample_recipe(user=self.user, title='Aubergine with tahini')

        tag1 = HelperSample.sample_tag(user=self.user, tag_name='Vegan')
        tag2 = HelperSample.sample_tag(user=self.user, tag_name='Vegetarian')

        recipe1.tag_fk.add(tag1)
        recipe2.tag_fk.add(tag2)
        recipe3 = HelperSample.sample_recipe(user=self.user, title='Fish and chips')

        # Testing API by making request for the 'Vegan' and 'Vegetarian' in our databse
        res = self.client.get(
            RECIPES_URL,
            {'tag_fk': f'{tag1.id},{tag2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        recipe1 = HelperSample.sample_recipe(user=self.user, title='Posh beans on toast')
        recipe2 = HelperSample.sample_recipe(user=self.user, title='Chicken cacciatore')

        ingredient1 = HelperSample.sample_ingredient(user=self.user, ing_name='Feta cheese')
        ingredient2 = HelperSample.sample_ingredient(user=self.user, ing_name='Chicken')

        recipe1.ingredient_fk.add(ingredient1)
        recipe2.ingredient_fk.add(ingredient2)
        recipe3 = HelperSample.sample_recipe(user=self.user, title='Steak and mushrooms')

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        # self.assertNotIn(serializer3.data, res.data)
