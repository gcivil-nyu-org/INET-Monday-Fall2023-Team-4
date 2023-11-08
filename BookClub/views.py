from django.shortcuts import render, redirect, get_object_or_404
from .models import BookClub
from .forms import BookClubForm, BookClubEditForm


def create_book_club(request):
    form = BookClubForm
    return render(request, "bookclub.html", {"form": form})


def edit_book_club(request, book_club_id):
    book_club = get_object_or_404(BookClub, id=book_club_id)

    if request.method == "POST":
        form = BookClubEditForm(request.POST, instance=book_club)
        if form.is_valid():
            new_admin = form.cleaned_data["admin"]
            if new_admin not in book_club.members.all():
                book_club.members.add(new_admin)
            form.save()
            return redirect("book_club_detail", book_club_id=book_club.id)
    else:
        form = BookClubEditForm(instance=book_club)

    return render(request, "bookclub_edit.html", {"form": form, "book_club": book_club})


def book_club_detail(request, book_club_id):
    book_club = get_object_or_404(BookClub, id=book_club_id)

    context = {
        "book_club": book_club,
    }

    return render(request, "bookclub_detail.html", context)
