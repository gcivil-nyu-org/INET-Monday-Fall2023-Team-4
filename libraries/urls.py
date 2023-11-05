from django.urls import path
from libraries.views import LibraryView, LibraryListView

app_name = "libraries"
urlpatterns = [
    path("<int:pk>", LibraryView.as_view(), name="library-detail"),
    path("", LibraryListView.as_view(), name="library-list"),
]
