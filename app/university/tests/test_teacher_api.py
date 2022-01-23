from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from university import models
from core.utils import HelperTest


CREATE_TEACHER_URL = reverse('university:create_teacher')


class TestPublicTeacherAPIRequests(TestCase):
    """Test for unauthenticated requests to teacher endpoints"""
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

        self.teacher_payload = {
            'user': self.user_payload,
            'salary': '1200.00',
            'subjects': []
        }

    def test_create_teacher_fail(self):
        """Test that authentication is required to create a teacher"""
        res = self.client.post(CREATE_TEACHER_URL,
                               self.teacher_payload,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        exists = models.Teacher.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)

    def test_create_teacher_forbiden(self):
        """Test creating a teacher with an user that is not allowed"""
        user = HelperTest.create_user(
            name='Test User',
            email='testemail@user.com',
            password='password'
        )
        self.client.force_authenticate(user=user)

        res = self.client.post(CREATE_TEACHER_URL,
                               self.teacher_payload,
                               format='json')

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        exists = models.Employee.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertFalse(exists)


class TestPrivateTeacherAPIRequests(TestCase):
    """Test for authenticated requests to teacher endpoints"""
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
            'email': 'teacher@email.com',
            'password': 'password',
            'cpf': '516.040.900-90',
            'phone': '19 99999-9999',
            'street': 'Rua Antonia Maria das Neves Carvalhos',
            'state': 'PE',
            'city': 'Caruaru',
            'zip_code': '55019-325',
        }
        self.teacher_payload = {
            'user': self.user_payload,
            'salary': '1200.00',
            'subjects': []
        }

    def test_create_teacher_success(self):
        """Test creating a teacher successfuly"""

        res = self.client.post(CREATE_TEACHER_URL,
                               self.teacher_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Teacher.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertTrue(exists)

    def test_create_teacher_with_credentials_already_registered(self):
        """Test creating a teacher with an email already registered"""
        HelperTest.create_user(**self.user_payload)
        res = self.client.post(CREATE_TEACHER_URL,
                               self.teacher_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test creating an employee short password"""
        self.user_payload['password'] = 'short'
        res = self.client.post(CREATE_TEACHER_URL,
                               self.teacher_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=self.user_payload['email']).exists()
        self.assertFalse(user_exists)

    def test_retrive_teacher_success(self):
        """Test get an especific teacher"""
        user = HelperTest.create_user(
            name='Test User',
            email='testuser@email.com',
            password='password'
        )
        teacher = models.Teacher.objects.create(
            user=user,
            salary='2500.00',
        )
        GET_TEACHER_URL = reverse(
            'university:retrive_teacher',
            kwargs={'pk': teacher.pk}
        )

        res = self.client.get(GET_TEACHER_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(teacher.user.email, res.data['user']['email'])

    def test_delete_teacher(self):
        """Test deleting an especifi teacher"""
        user = HelperTest.create_user(
            name='Test User',
            email='testuser@email.com',
            password='password'
        )
        teacher = models.Teacher.objects.create(
            user=user,
            salary='2500.00',
        )
        GET_TEACHER_URL = reverse(
            'university:retrive_teacher',
            kwargs={'pk': teacher.pk}
        )
        res = self.client.delete(GET_TEACHER_URL)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = models.Teacher.objects.filter(
            id=teacher.id
        ).exists()
        self.assertFalse(exists)

    def test_update_full_teacher(self):
        """Test updating all the fields of a teacher (PUT)"""
        user = HelperTest.create_user(
            name='Test User',
            email='testuser@email.com',
            password='password'
        )
        teacher = models.Teacher.objects.create(
            user=user,
            salary='2500.00',
        )
        GET_TEACHER_URL = reverse(
            'university:retrive_teacher',
            kwargs={'pk': teacher.pk}
        )
        update_payload = {
            'user': {
                'name': 'Test Update',
                'email': 'update@teacher.com',
                'password': 'newpassword',
                'cpf': '015.207.600-00',
                'phone': '11 99999-8888',
                'street': 'Beco Antônio Pinto',
                'state': 'AM',
                'city': 'Manaus',
                'zip_code': '69063-420',
                'complement': ''
            },
            'hired_date': date.today(),
            'salary': '5400.00',
            'subjects': [
                models.Subject.objects.create(
                    name='Update Subject1').id,
                models.Subject.objects.create(
                    name='Update Subject2').id,
            ]
        }

        res = self.client.put(
            GET_TEACHER_URL,
            update_payload,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        teacher.refresh_from_db()
        self.assertEqual(teacher.user.email, update_payload['user']['email'])
        self.assertEqual(teacher.user.name, update_payload['user']['name'])
        self.assertEqual(
            teacher.user.complement,
            update_payload['user']['complement']
        )

    def test_update_partial_teacher(self):
        """Test updating some fields of a teacher (PATCH)"""
        user = HelperTest.create_user(
            name='Test User',
            email='testuser@email.com',
            password='password'
        )
        teacher = models.Teacher.objects.create(
            user=user,
            salary='2500.00',
        )
        GET_TEACHER_URL = reverse(
            'university:retrive_teacher',
            kwargs={'pk': teacher.pk}
        )
        update_payload = {
            'user': {
                'name': 'Test Update',
                'email': 'update@teacher.com',
                'complement': 'New Complement'
            },
            'salary': '5400.00'
        }

        res = self.client.patch(
            GET_TEACHER_URL,
            update_payload,
            format='json'
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        teacher.refresh_from_db()
        self.assertEqual(
            teacher.user.email,
            update_payload['user']['email']
        )
        self.assertEqual(teacher.user.name, update_payload['user']['name'])
        self.assertEqual(
            teacher.user.complement,
            update_payload['user']['complement']
        )

    def test_update_password(self):
        """Testing update a password from an teacher instance"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        teacher = models.Teacher.objects.create(
            user=user,
            salary='1200.00',
        )
        password = 'newpassword'
        update_payload = {
            'user': {
                'password': password
            }
        }
        GET_TEACHER_URL = reverse(
                'university:retrive_teacher',
                kwargs={'pk': teacher.pk}
            )

        self.client.patch(
            GET_TEACHER_URL,
            update_payload,
            format='json'
        )
        teacher.refresh_from_db()
        self.assertTrue(
            teacher.user.check_password(password)
        )
