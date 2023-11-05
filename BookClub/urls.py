from django.urls import path
from .views import create_book_club

urlpatterns = [
    path("create/", create_book_club, name="create-book-club"),
]
