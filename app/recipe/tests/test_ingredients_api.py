import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test the publically available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access this endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test ingredients can be retrieved by authorized user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            os.environ.get('USER_EMAIL'),
            os.environ.get('USER_PASS')
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(useraccount=self.user, ing_name='kale')
        Ingredient.objects.create(useraccount=self.user, ing_name='Salt')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-ing_name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Ingredient.objects.create(useraccount=user2, ing_name='Vinegar')

        ingredient = Ingredient.objects.create(useraccount=self.user, ing_name='Tumeric')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['ing_name'], ingredient.ing_name)

    # below 2 function will test create and exist of Ingredients
    # it will access recipe/views/perform_create() and get_queryset() respectively
    def test_create_ingredients_successful(self):
        """Test create a new ingredient"""
        payload = {'ing_name': 'Cabbage'}  # Manually providing details for unittest
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(useraccount=self.user,
                                           ing_name=payload['ing_name'],
                                           ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'ing_name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Add tests for filtering ingredients
    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(useraccount=self.user, ing_name='Apples')
        ingredient2 = Ingredient.objects.create(useraccount=self.user, ing_name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=9.9,
            useraccount=self.user
        )
        recipe.ingredient_fk.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredient_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(useraccount=self.user, ing_name='Eggs')
        Ingredient.objects.create(useraccount=self.user, ing_name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs benedict',
            time_minutes=30,
            price=9.00,
            useraccount=self.user
        )
        recipe1.ingredient_fk.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Green eggs on toast',
            time_minutes=20,
            price=5.00,
            useraccount=self.user
        )
        recipe2.ingredient_fk.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)