from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_signup, name='user_signup'),  # User sign-up page
    path('login/', views.login_view, name='login'),  # Login page
    path('password_reset/', views.password_reset, name='password_reset'),
    path('profile/', views.profile_view, name='profile'),
    path('tasks/<int:task_id>/complete/', views.mark_task_complete, name='mark_task_complete'),
    path('upload/', views.upload_content, name='upload_content'),
    path('submit_answer/<int:content_id>/', views.submit_answer, name='submit_answer'),
]
