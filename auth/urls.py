from django.urls import path
from .views import register, login, request_reset, reset_password

urlpatterns = [
    path("register/", register),
    path("login/", login),
    path("request-reset/", request_reset),
    path("reset-password/", reset_password),
]