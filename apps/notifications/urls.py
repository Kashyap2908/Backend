from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_notifications, name="notifications-list"),
    path("<uuid:notification_id>/read/", views.mark_read, name="notifications-mark-read"),
    path("read-all/", views.mark_all_read, name="notifications-mark-all-read"),
]
