from django.urls import path

from . import views


app_name = "university"

urlpatterns = [
    path(
            'employee/',
            views.CreateListEmployeeAPIView.as_view(),
            name="create_list_employee"
        ),
    path(
            'retrive-employee/<uuid:pk>',
            views.RetriveEmployeeAPIView.as_view(),
            name='retrive_employee'
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
        ),
    path(
            'lesson/',
            views.CreateLessonAPIView.as_view(),
            name='create_lesson'
        )
]
