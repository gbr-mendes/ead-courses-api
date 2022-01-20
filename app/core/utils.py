from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from university.models import Employee


class HelperTest:
    @staticmethod
    def create_user(**params):
        return get_user_model().objects.create_user(**params)

    @staticmethod
    def create_superuser(email, password):
        return get_user_model().objects.create_superuser(email, password)

    @staticmethod
    def create_employee(**params):
        return Employee.objects.create(**params)

    @staticmethod
    def create_allowed_groups(groups):
        for group in groups:
            Group.objects.create(name=group)

    @staticmethod
    def add_user_allowed_group(user, allowed_groups):
        allowed = False
        user_groups = user.groups.all()
        for group in user_groups:
            if group.name in allowed_groups:
                return
        if not allowed:
            user.groups.add(Group.objects.get(name=allowed_groups[0]))
