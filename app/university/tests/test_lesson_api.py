from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from university import models
from core.utils import HelperTest

CREATE_LESSON_URL = reverse('university:create_lesson')


class PublicLessonAPITest(TestCase):
    """Tests from uanthenticated requests to lesson endpoint"""
    def setUp(self):
        self.client = APIClient()

        self.lesson_payload = {
            'subject': models.Subject.objects.create(name='Test Subject').id,
            'title': 'Test Lesson',
            'textual_content': 'Some text content',
            'video_url': ''
        }

    def test_create_lesson_unauthorized(self):
        """Test creating a lesson with an unahtenticated user"""
        res = self.client.post(CREATE_LESSON_URL, self.lesson_payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_forbidden(self):
        """Test creating a lesson with an user without valid privilegies"""
        user = HelperTest.create_user(
            email='test@email.com',
            password='password'
        )
        self.client.force_authenticate(user=user)
        res = self.client.post(CREATE_LESSON_URL, self.lesson_payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateLessonApiTest(TestCase):
    """Tests from authenticated users to lesson endpoint"""
    def setUp(self):
        self.client = APIClient()
        self.user = HelperTest.create_user(
            name='Test User Teacher',
            email='test@testteacher.com',
            password='password'
        )
        self.teacher = models.Teacher.objects.create(
            user=self.user,
            salary='1200.00',
        )
        self.subjects = [
            models.Subject.objects.create(name='Subject 1'),
            models.Subject.objects.create(name='Subject 2'),
        ]
        self.teacher.subjects.set(self.subjects)

        allowed_groups = ('Teachers',)
        HelperTest.create_allowed_groups(allowed_groups)
        HelperTest.add_user_allowed_group(self.user, allowed_groups)

        self.client.force_authenticate(user=self.user)

        self.lesson_payload = {
            'title': 'Lesson Title',
            'textual_content': 'Textual content test',
            'video_url': '',
            'subject': self.subjects[0].id
        }

    def test_create_lesson_success(self):
        """Test creating a lesson successfuly"""
        res = self.client.post(CREATE_LESSON_URL, self.lesson_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Lesson.objects.filter(
            id=res.data['id']
        )
        self.assertTrue(exists)

    def test_create_lesson_subject_off(self):
        """Test creating a lesson for a subject off the teacher set"""
        subject = models.Subject.objects.create(name='Subject off')
        self.lesson_payload['subject'] = subject

        res = self.client.post(CREATE_LESSON_URL, self.lesson_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
