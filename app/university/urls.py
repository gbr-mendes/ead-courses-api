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
            'retrive-teacher/<uuid:pk>',
            views.RetriveTeacherAPIView.as_view(),
            name='retrive_teacher'
        ),
    path(
        'student/',
        views.CreateStudentAPIView.as_view(),
        name='create_student'
        ),
    path(
            'retrive-student/<uuid:pk>',
            views.RetriveStudentAPIView.as_view(),
            name='retrive_student'
        ),
    path(
            'course/',
            views.CreateCourseAPIView.as_view(),
            name='create_course'
        ),
    path(
            'retrive-course/<uuid:pk>',
            views.RetriveCourseAPIView.as_view(),
            name='retrive_course'
        ),
    path(
            'lesson/',
            views.CreateLessonAPIView.as_view(),
            name='create_lesson'
        ),
    path(
            'watch-course/<uuid:pk>',
            views.WatchCourseAPIView.as_view(),
            name='watch_course'
        ),
    path(
            'create-subject/',
            views.CreateSubjectAPIView.as_view(),
            name='create_subject'
        )
]
