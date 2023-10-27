from django.urls import path

from . import views

app_name = "libraries"
urlpatterns = [
    path("", views.index, name="index"),
]
