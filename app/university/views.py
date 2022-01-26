from rest_framework import generics, exceptions

from university.serializers import (
                                        EmployeeSerializer,
                                        StudentSerializer,
                                        SubjectSerializer,
                                        TeacherSerializer,
                                        CourseSerializer,
                                        LessonSerializer
                                    )
from university.permissions import SchoolAdministrators, Teachers, Students
from university import models


class CreateListEmployeeAPIView(generics.ListCreateAPIView):
    """Create a new employee in the system"""
    serializer_class = EmployeeSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Employee.objects.all()


class RetriveEmployeeAPIView(
                                generics.DestroyAPIView,
                                generics.RetrieveUpdateAPIView
                            ):
    """Retrive an especific employee"""
    serializer_class = EmployeeSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Employee.objects.all()


class CreateTeacherAPIView(generics.ListCreateAPIView):
    """Create a new Teacher in the system"""
    serializer_class = TeacherSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Teacher.objects.all()


class RetriveTeacherAPIView(
                                    generics.RetrieveUpdateAPIView,
                                    generics.DestroyAPIView
                              ):
    """Retrive an especific teacher"""
    serializer_class = TeacherSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Teacher.objects.all()


class CreateStudentAPIView(generics.ListCreateAPIView):
    """Create a new student in the system"""
    serializer_class = StudentSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Student.objects.all()


class RetriveStudentAPIView(
        generics.RetrieveUpdateAPIView,
        generics.DestroyAPIView
        ):
    serializer_class = StudentSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Student.objects.all()


class CreateCourseAPIView(generics.ListCreateAPIView):
    """Create a new Course on de system"""
    serializer_class = CourseSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Course.objects.all()


class RetriveCourseAPIView(
        generics.RetrieveUpdateAPIView,
        generics.DestroyAPIView
        ):
    """Retrive an especific course"""
    serializer_class = CourseSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Course.objects.all()


class CreateLessonAPIView(generics.CreateAPIView, generics.ListAPIView):
    """Create a new lesson on the system"""
    serializer_class = LessonSerializer
    permission_classes = (Teachers,)
    queryset = models.Lesson.objects.all()


class WatchCourseAPIView(generics.RetrieveAPIView):
    """Restrive a course to a student"""
    serializer_class = CourseSerializer
    permission_classes = (Students,)
    queryset = models.Course.objects.all()

    def get_object(self):
        try:
            queryset = super().get_object()
            user = self.request.user
            student = models.Student.objects.get(user=user)
            if student.course != queryset:
                raise exceptions.PermissionDenied(
                    'The student can only access the course in which he is enrolled',
                    )

            return queryset
        except exceptions.PermissionDenied as e:
             raise e
        except:
            raise exceptions.PermissionDenied('Only students can watch a course')


class CreateSubjectAPIView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = (SchoolAdministrators,)
    queryset = models.Subject.objects.all()


class WatchLessonAPIVIew(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = (Students,)
    queryset = models.Lesson.objects.all()

    def get_object(self):
        queryset = super().get_object()
        try:
            student = models.Student.objects.get(
                user=self.request.user
            )
            course = student.course
            subjects = course.subjects.all()
            exists = False
            for subject in subjects:
                exists = models.Lesson.objects.filter(
                    subject=subject
                ).exists()
                if exists:
                    break

            if not exists:
                raise exceptions.PermissionDenied(
                    'The student can only access the lessons of the course in which he is enrolled'
                )
            return queryset
        except exceptions.PermissionDenied as e:
            raise e
        except:
            raise exceptions.PermissionDenied(
                    'Only a student can watch a lesson'
                )