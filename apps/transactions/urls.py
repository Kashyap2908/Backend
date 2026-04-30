from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_transactions, name="transactions-list"),
    path("<uuid:transaction_id>/", views.get_transaction, name="transactions-detail"),
    path("create/", views.create_transaction, name="transactions-create"),
    path("<uuid:transaction_id>/void/", views.void_transaction, name="transactions-void"),
]
