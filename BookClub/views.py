from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookClubForm, BookClubEditForm
from .models import BookClub
from django.contrib import messages


def book_club_details(request, slug):
    bc = BookClub.objects.get(id=slug)
    context = {
        "bookclub": bc,
        "member_count": bc.members.all().count(),
        "subscribed": bc.members.contains(request.user)
        if request.user.is_authenticated
        else False,
    }
    if request.method == "POST":
        if "subscribe" in request.POST:
            if (bc.libraryId.NYU == "0") or (
                bc.libraryId.NYU == "1" and request.user.status == "nyu"
            ):
                bc.members.add(request.user)
            else:
                messages.error(
                    request, "You must be a NYU student to subscribe to this book club"
                )
            return redirect("bookclub:details", slug=slug)
        elif "unsubscribe" in request.POST:
            bc.members.remove(request.user)
            return redirect("bookclub:details", slug=slug)
    return render(request, "details.html", context)


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
