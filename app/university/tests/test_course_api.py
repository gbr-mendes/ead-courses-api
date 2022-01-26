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

    def test_retrive_course_success(self):
        """Test retrive course to allowed user"""
        course = models.Course.objects.create(name='Test Course')
        RETRIVE_COURSE_URL = reverse(
            'university:retrive_course',
            kwargs={'pk': course.pk}
        )
        res = self.client.get(RETRIVE_COURSE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(str(course.id), res.data['id'])

    def test_update_full_course(self):
        """Test update all fields course"""
        subjects = [
            models.Subject.objects.create(name='Subject 1').id,
            models.Subject.objects.create(name='Subject 2').id
        ]
        course = models.Course.objects.create(name='Test Course')
        course.subjects.set(subjects)
        course.save()
        subjects_payload = [
            models.Subject.objects.create(name='Subject Update1').id,
            models.Subject.objects.create(name='Subject Update2').id,
        ]
        course_payload = {
            'name': 'New Name Course',
            'subjects': subjects_payload
        }
        RETRIVE_COURSE_URL = reverse(
            'university:retrive_course',
            kwargs={'pk': course.pk}
        )
        res = self.client.put(
            RETRIVE_COURSE_URL,
            course_payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, course_payload['name'])
        self.assertEqual(len(res.data['subjects']), 2)

        subjects_id = []
        for subject in course.subjects.all():
            subjects_id.append(str(subject.id))

        for subject in res.data['subjects']:
            self.assertIn(str(subject), subjects_id)

    def test_update_partial_course(self):
        """Test updating some fileds of a course"""
        course = models.Course.objects.create(name='Test Course')
        course_payload = {
            'name': 'New Name Course'
        }
        RETRIVE_COURSE_URL = reverse(
            'university:retrive_course',
            kwargs={'pk': course.pk}
        )
        res = self.client.patch(
            RETRIVE_COURSE_URL,
            course_payload,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        course.refresh_from_db()
        self.assertEqual(course.name, course_payload['name'])


class WatchCourseAPITest(TestCase):
    """Tests fo requests to wtach course endpoint"""
    def setUp(self):
        self.client = APIClient()
        self.user = HelperTest.create_user(
            name='Student Name',
            email='student@email.com',
            password='password'
        )
        self.student = models.Student.objects.create(
            user=self.user,
            course=models.Course.objects.create(
                name='Test Course'
            )
        )
        self.client.force_authenticate(self.user)

    def test_watch_course_success(self):
        """Test student watch course success"""
        course = self.student.course
        COURSE_URL = reverse(
            'university:watch_course',
            kwargs={'pk': course.id}
        )
        res = self.client.get(COURSE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['id'], str(course.id))

    def test_watch_course_forbiden(self):
        """Test watch a course for a not allowed student"""
        new_course = models.Course.objects.create(
            name='New Course'
        )
        COURSE_URL = reverse(
            'university:watch_course',
            kwargs={'pk': new_course.id}
        )
        res = self.client.get(COURSE_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
