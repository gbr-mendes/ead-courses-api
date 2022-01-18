from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path('employee/', views.CreateEmployeeAPIView.as_view(), name="create_employee"),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManagerUserView.as_view(), name='me'),
]

