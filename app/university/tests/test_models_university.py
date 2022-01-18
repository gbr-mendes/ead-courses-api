from django.test import TestCase
from django.contrib.auth import get_user_model

from university import models


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class TestUniversityModels(TestCase):
    """Tests for University models"""
    def test_employee_str(self):
        """Test the employee string representaion"""
        employee = models.Employee.objects.create(
            user=create_user(
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
