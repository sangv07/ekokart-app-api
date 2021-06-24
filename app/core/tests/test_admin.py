from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    # SetUp function will run before every Test in Test CAses
    def setUp(self):
        print('***SetUP https://docs.djangoproject.com/en/3.2/topics/testing/tools/********')
        self.client = Client()
        # passing email and password to app/core/model/UserManger() is functions() and forced tp login
        self.admin_user = get_user_model().objects.create_superuser(
            email       = 'admin@appdev.com',
            first_name='test_first',
            last_name='test_last',
            username='test',
            password='admin123',
        )
        self.client.force_login(self.admin_user)

        # passing variable to create_user() in core/models
        self.user = get_user_model().objects.create_user(
            email       = 'test@appdev.com',
            password    = 'test123',
        )

    # Test Case to test superuser
    def test_users_listed(self):
        """Test that users are listed on user_page (Django admin)"""
        # When an AdminSite is deployed, the views provided by that site are accessible using Django’s URL reversing system.
        # https://docs.djangoproject.com/en/2.1/ref/contrib/admin/
        # Page	                URL name
        # Changelist	{{ app_label }}_{{ model_name }}_changelist
        url = reverse('admin:core_useraccount_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)


    def test_user_change_page(self):
        """Test that the user edit page works"""
        url = reverse('admin:core_useraccount_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_useraccount_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
