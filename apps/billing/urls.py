from django.urls import path
from . import views

urlpatterns = [
    path("invoices/", views.list_invoices, name="billing-invoices-list"),
    path("invoices/create/", views.create_invoice, name="billing-invoices-create"),
    path("invoices/<uuid:invoice_id>/", views.get_invoice, name="billing-invoices-detail"),
    path("invoices/<uuid:invoice_id>/pay/", views.mark_paid, name="billing-invoices-pay"),
]
