from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import Group

from rest_framework.test import APIClient
from rest_framework import status

from university import models

CREATE_EMPLOYEE_URL = reverse('university:create_employee')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_employee(**params):
    return models.Employee.objects.create(**params)


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

        self.employee_payload = {
            'user': self.user_payload,
            'salary': '1200.00',
            'job': models.Job.objects.create(name='Test Job').id
        }

    def test_create_employee_fail(self):
        """Test that authentication is required to create a employee"""
        self.employee_payload = {
            'user': self.user_payload,
            'salary': '1200.00',
            'job': models.Job.objects.create(name='Test Job').id
        }

        res = self.client.post(CREATE_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)

    def test_create_employee_forbiden(self):
        """Test creating an employee with an user that is not allowed"""

        user = create_user(
            name='Test User',
            email='testemail@user.com'
        )
        self.client.force_authenticate(user=user)
        res = self.client.post(CREATE_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)


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
            'salary': '1200.00',
            'job': models.Job.objects.create(name='Test Job').id
        }

    def test_create_employee_success(self):
        """Test creating an employee successfuly"""

        res = self.client.post(CREATE_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertTrue(exists)

    def test_create_employee_with_credentials_already_registered(self):
        """Test creating an employee with an email already registered"""
        create_user(**self.user_payload)
        res = self.client.post(CREATE_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test creating an employee short password"""
        self.user_payload['password'] = 'short'
        res = self.client.post(CREATE_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=self.user_payload['email']).exists()
        self.assertFalse(user_exists)
