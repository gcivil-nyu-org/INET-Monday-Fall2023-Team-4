from django.shortcuts import get_object_or_404, render, redirect
from .forms import BookClubForm
from .models import BookClub
from .models import Library
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def create_book_club(request):
    library_id = request.GET.get('libraryId') or request.POST.get('libraryId')
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
                return render(request, "libraries/library_detail.html",{"library": library2})
        elif request.user.status != "nyu" and library.NYU == "1":
            messages.error(request, "You are not allowed to create a book club for NYU libraries.")

        else:
            if form.is_valid():
                library = Library.objects.get(id=int(library_id))    
                book_club = form.save(commit=False)
                book_club.admin = request.user
                book_club.libraryId = library
                book_club.save()
                book_club.members.add(request.user)
                library2 = get_object_or_404(Library, pk=library_id)
                return render(request, "libraries/library_detail.html",{"library": library2})
    else:
        form = BookClubForm()
    return render(request, "bookclub.html", {"form": form})
