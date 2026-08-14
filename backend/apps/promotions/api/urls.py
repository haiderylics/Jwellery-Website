"""URL routing for promotions public APIs."""

from django.urls import path

from .views import ActivePopupView, ActivePromotionsView

urlpatterns = [
    path("promotions/active/", ActivePromotionsView.as_view(), name="promotions-active"),
    path("popups/active/", ActivePopupView.as_view(), name="popups-active"),
]
