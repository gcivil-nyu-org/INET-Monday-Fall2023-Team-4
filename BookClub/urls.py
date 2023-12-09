from django.urls import path
from .views import (
    create_book_club,
    edit_book_club,
    book_club_details,
    error_page,
    voting_form,
    delete_book_club,
    deletion_confirmation,
)
from django.contrib.auth.decorators import login_required

# app_name = "bookclub"

urlpatterns = [
    path("error", error_page, name="error_page"),
    path("create", login_required(create_book_club), name="create-book-club"),
    path("delete", login_required(delete_book_club), name="delete_book_club"),
    path("delete/confirmation", deletion_confirmation, name="deletion_confirmation"),
    path("<slug:slug>", book_club_details, name="details"),
    path("<int:book_club_id>/edit", edit_book_club, name="edit_book_club"),
    path("voting/<slug:slug>", voting_form, name="voting"),
]
