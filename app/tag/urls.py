"""Module containing the url routing for the tags."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register("tags", views.TagViewSet)
router.register("children", views.ChildViewSet)

app_name = "tags"

urlpatterns = [
    path("", include(router.urls)),
]
