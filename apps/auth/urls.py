from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="auth-register"),
    path("login/", views.login, name="auth-login"),
    path("refresh/", views.refresh_token, name="auth-refresh"),
    path("logout/", views.logout, name="auth-logout"),
    path("request-reset/", views.request_reset, name="auth-request-reset"),
    path("reset-password/", views.reset_password, name="auth-reset-password"),
]
