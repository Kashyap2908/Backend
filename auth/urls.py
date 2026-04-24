from django.urls import path
from .views import login, request_reset, reset_password

urlpatterns = [
    path("login/", login),
    path("request-reset/", request_reset),
    path("reset-password/", reset_password),
]