from django.urls import path
from .views import create_book_club,book_club_details

appname="bookclub"
urlpatterns = [
    path("create/", create_book_club, name="create-book-club"),
	path("details/<slug:slug>/",book_club_details,name="details")
]
