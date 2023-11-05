from django.shortcuts import render
from .forms import BookClubForm


def create_book_club(request):
    form = BookClubForm
    return render(request, "bookclub.html", {"form": form})
