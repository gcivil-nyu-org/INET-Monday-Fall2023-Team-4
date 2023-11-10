from django.shortcuts import get_object_or_404, render, redirect
from .forms import BookClubEditForm, BookClubForm
from .models import BookClub
from .models import Library
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def create_book_club(request):
    library_id = request.GET.get("libraryId") or request.POST.get("libraryId")
    library = Library.objects.get(id=int(library_id))
    form = BookClubForm(request.POST or None)
    if request.method == "POST":
        if request.user.status == "nyu" and library.NYU == "1":
            if form.is_valid():
                book_club = form.save(commit=False)
                book_club.admin = request.user
                book_club.libraryId = library
                book_club.save()
                book_club.members.add(request.user)
                library2 = get_object_or_404(Library, pk=library_id)
                return render(
                    request, "libraries/library_detail.html", {"library": library2}
                )
        elif request.user.status != "nyu" and library.NYU == "1":
            messages.error(
                request, "You are not allowed to create a book club for NYU libraries."
            )

        else:
            if form.is_valid():
                library = Library.objects.get(id=int(library_id))
                book_club = form.save(commit=False)
                book_club.admin = request.user
                book_club.libraryId = library
                book_club.save()
                book_club.members.add(request.user)

                context = {
                    "book_club": book_club,
                }
                return render(request, "bookclub_detail.html", context)
    else:
        form = BookClubForm()
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
