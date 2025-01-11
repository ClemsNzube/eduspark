from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), 
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('calendar/', views.calendar, name='calendar'),
    path('grade/', views.grade, name='grade'),
    path('attendance/', views.attendance, name='attendance'),
    path('report/', views.report, name='report'),
    path('subject/<str:subject_name>/', views.subject_content, name='subject_content'),
]
