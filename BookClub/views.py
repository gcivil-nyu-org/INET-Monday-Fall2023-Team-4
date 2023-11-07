from django.shortcuts import render, redirect
from .forms import BookClubForm
from .models import BookClub
from .models import Library
from django.contrib.auth.decorators import login_required


@login_required
def create_book_club(request):
    if request.method == "POST":
        form = BookClubForm(request.POST)
        if form.is_valid():
            book_club = form.save(commit=False)
            book_club.admin = request.user
            book_club.libraryId = Library.objects.get(id=4)
            book_club.save()
            book_club.members.add(request.user)

    else:
        form = BookClubForm()
    return render(request, "bookclub.html", {"form": form})
