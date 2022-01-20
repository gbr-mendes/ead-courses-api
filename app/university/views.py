from rest_framework import generics

from university.serializers import (
                                        EmployeeSerializer,
                                        TeacherSerializer,
                                        CourseSerializer,
                                        LessonSerializer
                                    )
from university.permissions import SchoolAdministrators, Teachers
from university import models


class CreateEmployeeAPIView(generics.ListCreateAPIView):
    """Create a new employee in the system"""
    serializer_class = EmployeeSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Employee.objects.all()


class CreateTeacherAPIView(generics.ListCreateAPIView):
    """Create a new Teacher in the system"""
    serializer_class = TeacherSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Teacher.objects.all()


class CreateCourseAPIView(generics.ListCreateAPIView):
    """Create a new Course on de system"""
    serializer_class = CourseSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Course.objects.all()


class CreateLessonAPIView(generics.CreateAPIView):
    """Create a new lesson on the system"""
    serializer_class = LessonSerializer
    permission_classes = (Teachers,)
