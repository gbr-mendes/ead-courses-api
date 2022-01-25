from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from university import models


class HelperTest:
    @staticmethod
    def create_user(**params):
        return get_user_model().objects.create_user(**params)

    @staticmethod
    def create_superuser(email, password):
        return get_user_model().objects.create_superuser(email, password)

    @staticmethod
    def create_employee(**params):
        return models.Employee.objects.create(**params)

    @staticmethod
    def create_allowed_groups(groups):
        for group in groups:
            Group.objects.get_or_create(name=group)

    @staticmethod
    def add_user_allowed_group(user, allowed_groups):
        allowed = False
        user_groups = user.groups.all()
        for group in user_groups:
            if group.name in allowed_groups:
                return
        if not allowed:
            user.groups.add(Group.objects.get(name=allowed_groups[0]))

    @staticmethod
    def check_group_name_on_user_group_set(user, name):
        """Check a name on the group set of a user"""
        group_names = []
        for group in user.groups.all():
            group_names.append(group.name)
        if name in group_names:
            return True

    @staticmethod
    def create_multiples_employee(quantity):
        """Create multiples employee and return they email"""
        list_employee_email = []
        for count in range(0, quantity):
            user = get_user_model().objects.create_user(
                name=f'Test Name {count}',
                email=f'test{count}@testemail.com',
                password='password'
            )
            employee = models.Employee.objects.create(
                user=user,
                salary='1200.00',
                job=models.Job.objects.create(
                    name='Test Job'
                )
            )
            list_employee_email.append(employee.user.email)
        return list_employee_email

    @staticmethod
    def create_multiples_student(quantity):
        """Create multiples students and return they email"""
        list_student_email = []
        for count in range(0, quantity):
            user = get_user_model().objects.create_user(
                name=f'Test Name {count}',
                email=f'test{count}@testemail.com',
                password='password'
            )
            student = models.Student.objects.create(
                user=user,
                course=models.Course.objects.create(
                    name='Test Course'
                )
            )
            list_student_email.append(student.user.email)
        return list_student_email
