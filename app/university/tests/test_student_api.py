from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from university import models
from core.utils import HelperTest

CREATE_STUDENT_URL = reverse('university:create_student')


class PublicStudentAPITest(TestCase):
    """Test from unauthenticated\
    requests to student endpoints"""
    def setUp(self):
        self.client = APIClient()
        self.course = models.Course.objects.create(
            name='Course Name'
        )
        self.student_payload = {
            'user': {
                'name': 'Stundet Name',
                'email': 'student@email.com',
                'password': 'password'
            },
            'course': self.course.id
        }

    def test_create_student_fail(self):
        """Test creating a student with an unathenticated user"""
        res = self.client.post(
            CREATE_STUDENT_URL,
            self.student_payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        exists = models.Student.objects.filter(
            user__email=self.student_payload['user']['email']).exists()
        self.assertFalse(exists)

    def test_create_student_forbiden(self):
        """Test creating an student with an user that is not allowed"""

        user = HelperTest.create_user(
            name='Test User',
            email='testemail@user.com'
        )
        self.client.force_authenticate(user=user)
        res = self.client.post(CREATE_STUDENT_URL,
                               self.student_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        exists = models.Student.objects.filter(
            user__email=self.student_payload['user']['email']).exists()
        self.assertFalse(exists)


class PrivateStudentAPITest(TestCase):
    """Test creating a student with an authenticated user"""
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
        self.student_payload = {
            'user': self.user_payload,
            'course': models.Course.objects.create(name='Test Course').id
        }

    def test_create_student_success(self):
        """Test creating an student successfuly"""
        res = self.client.post(
            CREATE_STUDENT_URL,
            self.student_payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Student.objects.filter(
            user__email=self.user_payload['email']).exists()
        self.assertTrue(exists)

    def test_create_student_with_credentials_already_registered(self):
        """Test creating an student with an email already registered"""
        HelperTest.create_user(**self.user_payload)
        res = self.client.post(CREATE_STUDENT_URL,
                               self.student_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_too_short(self):
        """Test creating an student short password"""
        self.user_payload['password'] = 'short'
        res = self.client.post(CREATE_STUDENT_URL,
                               self.student_payload,
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects\
            .filter(email=self.user_payload['email']).exists()
        self.assertFalse(user_exists)

    def test_list_student_success(self):
        """Test listing student to allowed user"""
        quantity_student = 3
        list_student_email = HelperTest\
            .create_multiples_student(quantity_student)
        res = self.client.get(CREATE_STUDENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), quantity_student)

        for student in res.data:
            self.assertIn(student['user']['email'], list_student_email)

    def test_get_especific_student(self):
        """Test geting an especific student"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        student = models.Student.objects.create(
            user=user,
            course=models.Course.objects.create(name='Test Course')
        )
        GET_STUDENT_URL = reverse(
            'university:retrive_student',
            kwargs={'pk': student.pk}
        )
        res = self.client.get(GET_STUDENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(student.user.email, res.data['user']['email'])

    def test_delete_student(self):
        """Test deleting student"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        student = models.Student.objects.create(
            user=user,
            course=models.Course.objects.create(name='Test Course')
        )
        GET_STUDENT_URL = reverse(
            'university:retrive_student',
            kwargs={'pk': student.pk}
        )
        res = self.client.delete(GET_STUDENT_URL, args={'pk': student.pk})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = models.Student.objects.\
            filter(user__email=student.user.email).exists()
        self.assertFalse(exists)

    def test_student_full_update_success(self):
        """Test updating all fields for an student"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        student = models.Student.objects.create(
            user=user,
            course=models.Course.objects.create(name='Test Course')
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
        student_payload = {
            'user': user_payload,
            'course': models.Course.objects.create(name='Updated Course').id
        }
        GET_STUDENT_URL = reverse(
            'university:retrive_student',
            kwargs={'pk': student.pk}
        )
        res = self.client.put(
            GET_STUDENT_URL,
            student_payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        student.refresh_from_db()
        self.assertEqual(student.user.name, user_payload['name'])
        self.assertEqual(student.user.email, user_payload['email'])
        self.assertEqual(student.course.id, student_payload['course'])

    def test_update_partial_student(self):
        """Test updating some fields for an student"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        student = models.Student.objects.create(
            user=user,
            course=models.Course.objects.create(name='Test Course')
        )
        user_payload = {
            'email': 'email@testupdting.com',
            'cpf': '273.296.580-49',
        }
        student_payload = {
            'user': user_payload,
        }
        GET_STUDENT_URL = reverse(
            'university:retrive_student',
            kwargs={'pk': student.pk}
        )
        res = self.client.patch(
            GET_STUDENT_URL,
            student_payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        student.refresh_from_db()
        self.assertEqual(student.user.email, user_payload['email'])
        self.assertEqual(student.user.cpf, user_payload['cpf'])

    def test_update_password(self):
        """Testing update a password from an student instance"""
        user = HelperTest.create_user(
            name='Test Name',
            email='test@testemail.com',
            password='password'
        )
        student = models.Student.objects.create(
            user=user,
            course=models.Course.objects.create(name='Test Course')
        )
        password = 'newpassword'
        update_payload = {
            'user': {
                'password': password
            }
        }
        GET_STUDENT_URL = reverse(
            'university:retrive_student',
            kwargs={'pk': student.pk}
        )
        self.client.patch(
            GET_STUDENT_URL,
            update_payload,
            format='json'
        )
        student.refresh_from_db()
        self.assertTrue(
            student.user.check_password(password)
        )
