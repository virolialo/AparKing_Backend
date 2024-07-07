from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.user_reports, name='user-reports'),
    path('create/', views.user_report_create, name='user-report-create'),
]