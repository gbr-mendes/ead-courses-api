from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.utils import HelperTest

GENERATE_TOKEN_USER = reverse('accounts:token')
ME_URL = reverse('accounts:me')


class PublicUserApiTests(TestCase):
    """Test for unauthenticated requests"""
    def test_create_token_for_user(self):
        """Test creating a token successful for a valid user"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
                    'name': 'Test Case',
                    'password': 'testCase123'
                    }
        HelperTest.create_user(**payload)
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': 'testCase123'
            })

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creadentials(self):
        """Test that a token IS NOT generated with an invalid password"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
                    'password': 'testCase123'
                    }
        HelperTest.create_user(**payload)
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': 'wrong'
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that no token is created for a user that does not exists
        """
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'nouser@gbmsolucoesweb.com',
                'password': 'nouser'
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields_create_token(self):
        """Test that an email and password are requireds to create a token"""
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': ''
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """
        Test that authentication is required for retrive data of user
        """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test requests that require authentication"""
    def setUp(self):
        self.user = HelperTest.create_user(
            name='Test Name',
            email='authtest@user.com',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """
        Test retrive logged in user successuly
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, res.data['name'])
        self.assertEqual(self.user.email, res.data['email'])

    def test_post_me_not_allowed(self):
        """Test that posts requests are not allowed for the profile"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_profile_success(self):
        """
        Test that the user profile was updated
        """
        payload = {'name': 'Test Update Name', 'password': 'newpassword'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
