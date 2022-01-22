from django.test import TestCase

from university import models

from core.utils import HelperTest


class TestImplementedSignals(TestCase):
    """Tests for django signals ex: pre-save method"""
    def setUp(self):
        self.user = HelperTest.create_user(
            name='Test User',
            email='test@email.com',
            password='password'
        )

    def test_employee_added_to_group(self):
        """Test that the employee is added \
        to School Admin group after created (pos-save)"""
        HelperTest.create_employee(
            user=self.user,
            salary='1200.00',
            job=models.Job.objects.create(name='Test Job')
        )

        self.assertTrue(HelperTest .check_group_name_on_user_group_set(
            self.user,
            'School Admin'
        ))

    def test_teacher_added_to_group(self):
        """Test that a teacher is added \
        to Teacher groups after created (pos-save)"""
        models.Teacher.objects.create(
            user=self.user,
            salary='1200.00',
        )

        self.assertTrue(HelperTest.check_group_name_on_user_group_set(
            self.user,
            'Teachers'
        ))
