from django.urls import path
from . import views

urlpatterns = [
    path("<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
    path("<int:pk>/rate/", views.rate_book, name="rate_book"),
]
