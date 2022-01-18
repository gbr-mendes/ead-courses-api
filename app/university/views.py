from rest_framework import generics

from university.serializers import EmployeeSerializer
from university.permissions import SchoolAdministrators
from university import models


class CreateEmployeeAPIView(generics.ListCreateAPIView):
    """Create a new User in the system"""
    serializer_class = EmployeeSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Employee.objects.all()
