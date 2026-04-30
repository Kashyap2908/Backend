from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_summary, name="analytics-dashboard"),
    path("sales/", views.sales_report, name="analytics-sales"),
    path("stock/", views.stock_report, name="analytics-stock"),
    path("activity/", views.activity_logs, name="analytics-activity"),
]
