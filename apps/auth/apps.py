from django.apps import AppConfig


class NeuroAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "neuroauth"
    verbose_name = "Auth"
