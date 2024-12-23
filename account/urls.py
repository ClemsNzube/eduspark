from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_signup, name='user_signup'),  # User sign-up page
    path('login/', views.login_view, name='login'),  # Login page
    path('password_reset/', views.password_reset, name='password_reset'),
   
]
