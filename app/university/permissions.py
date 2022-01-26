from rest_framework import permissions


def is_in_multiple_groups(user, groups):
    return user.groups.filter(name__in=groups).exists()


class SchoolAdministrators(permissions.BasePermission):

    def has_permission(self, request, view):
        allowed_groups = ('School Admin',)
        if request.user.is_superuser:
            return True

        if is_in_multiple_groups(request.user, allowed_groups):
            return True

        return False


class Teachers(permissions.BasePermission):

    def has_permission(self, request, view):
        allowed_groups = ('Teachers',)
        if request.user.is_superuser:
            return True

        if is_in_multiple_groups(request.user, allowed_groups):
            return True

        return False


class Students(permissions.BasePermission):
    def has_permission(self, request, view):
        allowed_groups = ('Students',)
        if request.user.is_superuser:
            return True

        if is_in_multiple_groups(request.user, allowed_groups):
            return True

        return False
