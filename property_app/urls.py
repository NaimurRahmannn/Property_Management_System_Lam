from django.urls import path

from . import views

app_name = "property_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("api/locations/", views.location_autocomplete, name="location_autocomplete"),
]