from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from university import models
from core.utils import HelperTest

CREATE_LIST_EMPLOYEE_URL = reverse('university:create_list_employee')


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

        res = self.client.post(CREATE_LIST_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)

    def test_create_employee_forbiden(self):
        """Test creating an employee with an user that is not allowed"""

        user = HelperTest.create_user(
            name='Test User',
            email='testemail@user.com'
        )
        self.client.force_authenticate(user=user)
        res = self.client.post(CREATE_LIST_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)


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

        allowed_groups_list = ('School Admin',)
        HelperTest.create_allowed_groups(allowed_groups_list)
        HelperTest.add_user_allowed_group(self.user, allowed_groups_list)

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

        res = self.client.post(CREATE_LIST_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertTrue(exists)

    def test_create_employee_with_credentials_already_registered(self):
        """Test creating an employee with an email already registered"""
        HelperTest.create_user(**self.user_payload)
        res = self.client.post(CREATE_LIST_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test creating an employee short password"""
        self.user_payload['password'] = 'short'
        res = self.client.post(CREATE_LIST_EMPLOYEE_URL,
                               self.employee_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=self.user_payload['email']).exists()
        self.assertFalse(user_exists)

    def test_list_employee_success(self):
        """Test listing employees to allowed user"""
        quantity_employee = 3
        list_employee_email = HelperTest.create_multiples_employee(quantity_employee)
        res = self.client.get(CREATE_LIST_EMPLOYEE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), quantity_employee)
        
        for employee in res.data:
            self.assertIn(employee['user']['email'], list_employee_email)
    
    def test_get_especific_employee(self):
        """Test geting an especific employee"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        employee = HelperTest.create_employee(
            user=user,
            salary='1200.00',
            job=models.Job.objects.create(name='Test Job')
        )
        GET_EMPLOYEE_URL = reverse('university:retrive_employee', kwargs={'pk':employee.pk})
        res = self.client.get(GET_EMPLOYEE_URL, {'pk':employee.pk})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(employee.user.email, res.data['user']['email'])
    
    def test_delete_employee(self):
        """Test deleting employee"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        employee = HelperTest.create_employee(
            user=user,
            salary='1200.00',
            job=models.Job.objects.create(name='Test Job')
        )
        GET_EMPLOYEE_URL = reverse('university:retrive_employee', kwargs={'pk':employee.pk})
        res = self.client.delete(GET_EMPLOYEE_URL, args={'pk':employee.pk})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = models.Employee.objects.filter(user__email=employee.user.email).exists()
        self.assertFalse(exists)

    def test_employee_full_update_success(self):
        """Test updating all fields for an employee"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        employee = HelperTest.create_employee(
            user=user,
            salary='1200.00',
            job=models.Job.objects.create(name='Test Job')
        )
        user_payload = {
            'name': 'Test Updating',
            'email': 'email@testupdting.com',
            'password': 'passwordupd',
            'cpf': '273.296.580-49',
            'phone': '19 98888-8888',
            'street': 'Rua 1',
            'state': 'MG',
            'city': 'Belo Horizonte',
            'zip_code': '05170-120',
            'complement': 'Behind the national bank'
        }
        employee_payload = {
            'user': user_payload,
            'salary': '2500.00',
            'job': models.Job.objects.create(name='Updated Job').id
        }
        GET_EMPLOYEE_URL = reverse('university:retrive_employee', kwargs={'pk':employee.pk})
        res = self.client.put(GET_EMPLOYEE_URL, employee_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        employee.refresh_from_db()
        self.assertEqual(employee.user.name, user_payload['name'])
    
    def test_update_partial_employee(self):
        """Test updating some fields for an employee"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        employee = HelperTest.create_employee(
            user=user,
            salary='1200.00',
            job=models.Job.objects.create(name='Test Job')
        )
        user_payload = {
            'email': 'email@testupdting.com',
            'cpf': '273.296.580-49',
        }
        employee_payload = {
            'user': user_payload,
            'salary': '2500.00',
        }
        GET_EMPLOYEE_URL = reverse('university:retrive_employee', kwargs={'pk':employee.pk})
        res = self.client.patch(GET_EMPLOYEE_URL, employee_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        employee.refresh_from_db()
        self.assertEqual(employee.user.email, user_payload['email'])
