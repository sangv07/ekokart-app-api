import os

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
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
