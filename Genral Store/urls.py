from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ...existing code...
    # Optional: provide a login page at /accounts/login/ to satisfy any code that expects it
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # ...existing code...
]