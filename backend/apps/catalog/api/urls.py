"""URL routing for catalog public APIs."""

from django.urls import path

from .views import (
    AttributeTypeListView,
    CategoryListView,
    ProductDetailView,
    ProductListView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("attributes/", AttributeTypeListView.as_view(), name="attribute-list"),
]
