from django.urls import path
from .views import create_book_club

urlpatterns = [
    path('create/', create_book_club, name='create-book-club'),
    # Add other url patterns for the BookClub app here as needed
]