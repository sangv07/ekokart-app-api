import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user_tag = get_user_model().objects.create_user(
            os.environ.get('USER_EMAIL'),
            os.environ.get('USER_PASS')
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user_tag)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(useraccount=self.user_tag, tag_name='Vegan')
        Tag.objects.create(useraccount=self.user_tag, tag_name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-tag_name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Tag.objects.create(useraccount=user2, tag_name='Fruity')
        tag = Tag.objects.create(useraccount=self.user_tag, tag_name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['tag_name'], tag.tag_name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'tag_name': 'Simple'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            useraccount=self.user_tag,
            tag_name=payload['tag_name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid payload"""
        payload = {'tag_name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Add tests for filtering tags
    def test_retrieve_tags_assigned_to_recipes(self):
        """Test filtering tags by those assigned to recipes"""
        tag1 = Tag.objects.create(useraccount=self.user_tag, tag_name='Breakfast')
        tag2 = Tag.objects.create(useraccount=self.user_tag, tag_name='Lunch')
        recipe = Recipe.objects.create(
            title='Coriander eggs on toast',
            time_minutes=10,
            price=5.00,
            useraccount=self.user_tag,
        )
        recipe.tag_fk.add(tag1)

        # going to pass in this dictionary with the get parameters we want to apply it to
        # our get request and we're going to call our filter assigned only and if you pass in
        # a one then this will be evaluated to true and it will filter by the tags that are assigned only
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    # returning distinct set of tag
    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(useraccount=self.user_tag, tag_name='Breakfast')
        Tag.objects.create(useraccount=self.user_tag, tag_name='Lunch')
        recipe1 = Recipe.objects.create(
            title='Pancakes',
            time_minutes=5,
            price=3.00,
            useraccount=self.user_tag
        )
        recipe1.tag_fk.add(tag)
        recipe2 = Recipe.objects.create(
            title='Porridge',
            time_minutes=3,
            price=2.00,
            useraccount=self.user_tag
        )
        recipe2.tag_fk.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
