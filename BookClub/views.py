from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from .forms import BookClubForm


def create_book_club(request):
    return render(request, "bookclub.html", {})
