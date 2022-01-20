from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from university import models
from core.utils import HelperTest


CREATE_COURSE_URL = reverse('university:create_course')


class PublicCourseAPITest(TestCase):
    """Tests from unauthenticatedrequest to Course endpoint"""
    def setUp(self):
        self.client = APIClient()
        self.course_payload = {
            'name': 'Test Course',
            'subjects': []
        }

    def test_create_employee_unathorized(self):
        """Test creating a course with a unathenticated request"""
        res = self.client.post(CREATE_COURSE_URL, self.course_payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_course_forbidden(self):
        """Test creating a course with a unathorized user"""
        user = HelperTest.create_user(
            name='Test User',
            email='test@testcase.com',
            password='password'
        )
        self.client.force_authenticate(user=user)
        res = self.client.post(CREATE_COURSE_URL, self.course_payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateCourseAPITest(TestCase):
    """Test creating a ourse from allwed requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = HelperTest.create_user(
            name='Test User',
            email='test@testcase.com',
            password='password'
        )

        self.client.force_authenticate(user=self.user)

        allowed_groups_list = ('School Admin',)
        HelperTest.create_allowed_groups(allowed_groups_list)
        HelperTest.add_user_allowed_group(self.user, allowed_groups_list)

        self.course_payload = {
            'name': 'Test Course',
            'subjects': []
        }

    def test_create_course_success(self):
        """Test Creating a course successfuly"""
        res = self.client.post(CREATE_COURSE_URL, self.course_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        exists = models.Course.objects.filter(
            id=res.data['id']
        ).exists()
        self.assertTrue(exists)
