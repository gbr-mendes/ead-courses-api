from django.test import TestCase, Client
from django.urls import reverse
from core.utils import HelperTest


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = HelperTest.create_superuser(
            email='admin@gbmsolucoesweb.com',
            password='password123'
        )
        self.client.force_login(self.admin_user)
        self.user = HelperTest.create_user(
            email='test@gbmsolucoesweb.com',
            password='password123',
            name='Test User Full Name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:accounts_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user change page works"""
        url = reverse('admin:accounts_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test tha create user page works"""
        url = reverse('admin:accounts_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
