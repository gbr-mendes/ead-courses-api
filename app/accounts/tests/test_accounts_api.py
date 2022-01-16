from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import UserType

CREATE_USER_URL = reverse('accounts:create')
GENERATE_TOKEN_USER = reverse('accounts:token')
ME_URL = reverse('accounts:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicRoutesAccountsApiTest(TestCase):
    """Tests for an unauthenticated requests"""
    def setUp(self):
        self.client = APIClient()
        type_user = UserType.objects.create(name='Test Case User Type')
        self.payload = {
            'email': 'test@email.com',
            'password': 'TestCasePassWord',
            'name': 'Test Case',
            'type': type_user,
            'cpf': '204.782.150-96',
            'phone': '19999999999',
            'zip_code': '74603-110',
            'street': 'Rua 218',
            'city': 'Goiânia',
            'state': 'GO',
            'complement': '',
        }

    def test_create_user_unauthenticated(self):
        """Test creating an account with unauthenticated user"""
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_account_not_allowed_role(self):
        """
        Test creating an account with an authenticated user that
        is not on allowed groups
        """
        user = get_user_model().objects.create_user(
            email='teste@testecase.com',
            password='testecase1234'
        )
        self.client.force_authenticate(user=user)

        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_token_for_user(self):
        """Test creating a token successful for a valid user"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
                    'name': 'Test Case',
                    'password': 'testCase123'
                    }
        create_user(**payload)
        res = self.client.post(
            GENERATE_TOKEN_USER,
            {
                'email': 'test@gbmsolucoesweb.com',
                'password': 'testCase123'
            })

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_creadentials(self):
        """Test that a toke IS NOT generated with an invalid password"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
                    'name': 'Test Case',
                    'password': 'testCase123'
                    }
        create_user(**payload)
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
        Test that authentication is reqquiired for retrive data of user
        """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test requests that require authentication
    """
    def setUp(self):
        payload = {
                'name': 'Test Case',
                'email': 'testcase@gbmsolucoesweb.com',
                'password': 'testCase'}
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        type_user = UserType.objects.create(name='Test Case User Type')
        self.payload = {
            'email': 'test@email.com',
            'password': 'TestCasePassWord',
            'name': 'Test Case',
            'type': type_user.id,
            'cpf': '204.782.150-96',
            'phone': '19 99999-9999',
            'zip_code': '74603-110',
            'street': 'Rua 218',
            'city': 'Goiânia',
            'state': 'GO',
            'complement': '',
        }

    def test_create_user_success(self):
        """Test creating a user with sucessful"""
        allowed_group = Group.objects.get_or_create(name='School Admin')[0]
        self.user.groups.add(allowed_group.id)

        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            get_user_model().objects.filter(**res.data).exists()
        )

    def test_create_user_with_credentials_already_registered(self):
        """Test creating a user with an email already registered"""
        create_user(email='test@email.com', password='TestCasePassWord')
        allowed_group = Group.objects.get_or_create(name='School Admin')[0]
        self.user.groups.add(allowed_group.id)
        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """
        Test that a user is not created with a password
        less than 7 characters
        """

        self.payload['password'] = 'abc'
        allowed_group = Group.objects.get_or_create(name='School Admin')[0]
        self.user.groups.add(allowed_group.id)

        res = self.client.post(CREATE_USER_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=self.payload['email']).exists()
        self.assertFalse(user_exists)

    def test_retrive_profile_success(self):
        """
        Test retrive logged in user successul
        """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, res.data['name'])
        self.assertEqual(self.user.email, res.data['email'])

    def test_post_me_not_allowed(self):
        """
        Test that posts requests are not allowed for the profile
        """
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

    def test_create_user_invalid_cpf(self):
        allowed_group = Group.objects.get_or_create(name='School Admin')[0]
        self.user.groups.add(allowed_group.id)
        self.payload['cpf'] = 'invalid'
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_phone(self):
        allowed_group = Group.objects.get_or_create(name='School Admin')[0]
        self.user.groups.add(allowed_group.id)
        self.payload['phone'] = 'invalid'
        res = self.client.post(CREATE_USER_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
