from django.urls import path

from . import views


app_name = "university"

urlpatterns = [
    path(
            'employee/',
            views.CreateEmployeeAPIView.as_view(),
            name="create_employee"
        ),
    path(
            'teacher/',
            views.CreateTeacherAPIView.as_view(),
            name='create_teacher'
        ),
    path(
            'course/',
            views.CreateCourseAPIView.as_view(),
            name='create_course'
        )
]
