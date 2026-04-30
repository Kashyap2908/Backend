from django.contrib import admin
from django.urls import path, include
from neurostock.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    # Auth
    path("api/auth/", include("apps.auth.urls")),
    # Domain modules
    path("api/products/", include("apps.inventory.urls")),
    path("api/transactions/", include("apps.transactions.urls")),
    path("api/billing/", include("apps.billing.urls")),
    path("api/dashboard/", include("apps.analytics.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
]