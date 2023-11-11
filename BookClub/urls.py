from django.urls import path
from .views import create_book_club, edit_book_club, book_club_detail
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("create/", login_required(create_book_club), name="create-book-club"),
    path("details/<slug:slug>/", book_club_detail, name="details"),
    path("<int:book_club_id>/edit/", edit_book_club, name="edit_book_club"),
    path("<int:book_club_id>/", book_club_detail, name="book_club_detail"),
]
