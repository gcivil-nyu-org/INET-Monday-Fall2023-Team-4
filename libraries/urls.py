from django.urls import path
from libraries.views import LibraryDetailView, LibraryListView

app_name = "libraries"
urlpatterns = [
    path("<int:pk>", LibraryDetailView.as_view(), name="library-detail"),
    path("", LibraryListView.as_view(), name="library-list"),
]
