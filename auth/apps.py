from django.apps import AppConfig


class NeuroAuthConfig(AppConfig):
    """
    Project auth app. Label must differ from django.contrib.auth's "auth" label.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth"
    label = "neuroauth"
    verbose_name = "Auth"
