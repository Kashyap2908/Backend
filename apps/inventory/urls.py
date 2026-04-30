from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_products, name="inventory-list"),
    path("<uuid:product_id>/", views.get_product, name="inventory-detail"),
    path("create/", views.create_product, name="inventory-create"),
    path("<uuid:product_id>/update/", views.update_product, name="inventory-update"),
    path("<uuid:product_id>/delete/", views.delete_product, name="inventory-delete"),
    path("stock/", views.stock_summary, name="inventory-stock-summary"),
]
