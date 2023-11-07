from django.urls import path
from .views import create_book_club
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("create/", login_required(create_book_club), name="create-book-club"),
]
