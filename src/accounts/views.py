from django.shortcuts import render
from django.urls import reverse

from django.views.generic import CreateView
from django.contrib.auth.forms  import UserCreationForm

class UserRegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = 'user_registration.html'

    def get_success_url(self):
        return reverse('links:home')
