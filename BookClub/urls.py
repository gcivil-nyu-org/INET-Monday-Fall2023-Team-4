from django.urls import path
from .views import create_book_club, edit_book_club, book_club_details
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("create/", login_required(create_book_club), name="create-book-club"),
    path("<slug:slug>/", book_club_details, name="details"),
    path("<int:book_club_id>/edit/", edit_book_club, name="edit_book_club"),
]
