from django.urls import path
from . import views

urlpatterns = [
    # path('grades/performance/', views.student_performance, name='student_performance'),
    # path('grades/students/', views.teacher_view_students, name='teacher_view_students'),
    path('grades/student/', views.student_grades, name='student_grades'),
    path('grades/teacher/', views.teacher_grades, name='teacher_grades'),
    path('grades/parent/', views.parent_grades, name='parent_grades'),
]

