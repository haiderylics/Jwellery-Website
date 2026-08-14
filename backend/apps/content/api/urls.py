"""URL routing for content public APIs."""

from django.urls import path

from .views import AboutSectionView, GalleryItemListView, ReviewListView

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="review-list"),
    path("gallery/", GalleryItemListView.as_view(), name="gallery-list"),
    path("about/", AboutSectionView.as_view(), name="about-detail"),
]
