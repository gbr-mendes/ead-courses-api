import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import Group
from django.utils import timezone, dateformat

from rest_framework.test import APIClient
from rest_framework import status

from accounts import models, serializers

CREATE_EMPLOYEE_URL = reverse('accounts:create_employee')
GENERATE_TOKEN_USER = reverse('accounts:token')
ME_URL = reverse('accounts:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)

def create_employee(**params):
    return models.Employe.objects.create(**params)

def create_allowed_groups(groups):
    for group in groups:
        Group.objects.create(name=group)

def add_user_allowed_group(user, allowed_groups):
    allowed = False
    user_groups = user.groups.all()
    for group in user_groups:
        if group.name in allowed_groups:
            return
    if not allowed:
        user.groups.add(Group.objects.get(name=allowed_groups[0]))




class PublicUserApiTests(TestCase):
    """Test for unauthenticated requests"""
    def setUp(self):
        self.client = APIClient()
        self.user_payload = {
            'name': 'Test Case',
            'email': 'test@email.com',
            'password': 'password',
            'cpf': '516.040.900-90',
            'phone': '19 99999-9999',
            'street': 'Rua Antonia Maria das Neves Carvalhos',
            'state': 'PE',
            'city': 'Caruaru',
            'zip_code': '55019-325',
        }
    
    def test_create_employee_fail(self):
        """Test that authentication is required to create a employee"""
        employee_payload = {
            'user': self.user_payload,
            'hired_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'salary': '1200.00',
            'job': models.Job.objects.create(name='Test Job').id
        }

        res = self.client.post(CREATE_EMPLOYEE_URL, employee_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        exists = models.Employe.objects.filter(user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)

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
        """Test that a token IS NOT generated with an invalid password"""
        payload = {
                    'email': 'test@gbmsolucoesweb.com',
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
        Test that authentication is required for retrive data of user
        """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test requests that require authentication"""
    def setUp(self):
        self.user = create_user(
            name='Test Name',
            email='authtest@user.com',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        allowed_groups_list = ('School Admin',)
        create_allowed_groups(allowed_groups_list)
        add_user_allowed_group(self.user, allowed_groups_list)

        self.user_payload = {
            'name': 'Test Case',
            'email': 'test@email.com',
            'password': 'password',
            'cpf': '516.040.900-90',
            'phone': '19 99999-9999',
            'street': 'Rua Antonia Maria das Neves Carvalhos',
            'state': 'PE',
            'city': 'Caruaru',
            'zip_code': '55019-325',
        }
        self.employee_payload = {
            'user': self.user_payload,
            'hired_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'salary': '1200.00',
            'job': models.Job.objects.create(name='Test Job').id
        }
    def test_create_employee_success(self):
        """Test creating an employee successfuly"""
        
        res = self.client.post(CREATE_EMPLOYEE_URL,self.employee_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Employe.objects.filter(user__email=self.user_payload['email']).exists()
        self.assertTrue(exists)
    
    def test_create_user_with_credentials_already_registered(self):
        """Test creating an employee with an email already registered"""
        create_user(**self.user_payload)
        res = self.client.post(CREATE_EMPLOYEE_URL, self.employee_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_is_too_short(self):
        """Test creating an employee short password"""
        self.user_payload['password'] = 'short'
        res = self.client.post(CREATE_EMPLOYEE_URL, self.employee_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=self.user_payload['email']).exists()
        self.assertFalse(user_exists)
    
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
        