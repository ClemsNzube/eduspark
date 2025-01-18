from django.urls import path
from . import views

urlpatterns = [
    # Add the URL pattern for the student performance view
    path('performance/', views.student_performance, name='student_performance'),
]
