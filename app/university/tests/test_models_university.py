from django.test import TestCase

from university import models
from core.utils import HelperTest


class TestUniversityModels(TestCase):
    """Tests for University models"""
    def test_employee_str(self):
        """Test the employee string representaion"""
        employee = models.Employee.objects.create(
            user=HelperTest.create_user(
                email='test@emailtest.com',
                password='password',
                name='Test name'
            ),
            salary='1200.00',
            job=models.Job.objects.create(
                name='Job Test'
            )

        )
        self.assertEqual(str(employee), employee.user.name)

    def test_job_str(self):
        """Test the job string representaion"""
        job = models.Job.objects.create(
            name='Test Job'
        )
        self.assertEqual(str(job), job.name)

    def test_teacher_str(self):
        """Test the techer string representation"""
        user = HelperTest.create_user(
                email='test@emailtest.com',
                password='password',
                name='Test name'
            )
        teacher = models.Teacher.objects.create(
            user=user,
            salary='1200.00',
        )
        self.assertEqual(str(teacher), user.name)

    def test_subject_str(self):
        """Test the subject string repreentation"""
        name = 'Test Subject'
        subject = models.Subject.objects.create(name=name)
        self.assertEqual(str(subject), name)

    def test_course_str(self):
        """Test the course string representation"""
        name = 'Test Course'
        course = models.Course.objects.create(name=name)
        self.assertEqual(str(course), name)

    def test_lesson_str(self):
        """Test the lesson string respresentation"""
        title = 'Test Lesson'
        subject = models.Subject.objects.create(name='Test Subject')
        lesson = models.Lesson.objects.create(
            title=title,
            textual_content='Text Lesson',
            subject=subject

        )
        self.assertEqual(str(lesson), title)
