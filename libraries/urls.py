from django.urls import path

from . import views
from libraries.views import LibraryDetailView, LibraryListView

app_name = "libraries"
urlpatterns = [
    # path("", views.index, name="index"),
    path("<slug:slug>/", LibraryDetailView.as_view(), name="library-detail"),
    path("", LibraryListView.as_view(), name="library-list"),
]
