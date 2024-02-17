"""Defines URL patterns for accounts app"""

from django.urls import path

from django.contrib.auth.views import LoginView, LogoutView
from .views import UserRegistrationView

app_name='accounts'
urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', UserRegistrationView.as_view(), name='register'),
]