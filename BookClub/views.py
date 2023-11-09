from django.shortcuts import render, redirect
from .forms import BookClubForm
from .models import BookClub
from libraries.models import Library
from django.contrib import messages


def book_club_details(request,slug):
    bc = BookClub.objects.get(id=slug)
    context = {
		'bookclub': bc,
		'member_count': bc.members.all().count(),
		'subscribed': bc.members.contains(request.user)
    }
    print(context)
    if request.method == "POST":
        if 'subscribe' in request.POST:
            if (bc.libraryId.NYU == '0') or (bc.libraryId.NYU == '1' and request.user.status == 'nyu'):
                bc.members.add(request.user)
            else:
                messages.error(
                request,
                "You must be a NYU student to subscribe to this book club"
            )
            return redirect("bookclub:details",slug=slug)
        elif 'unsubscribe' in request.POST:
            bc.members.remove(request.user)
            return redirect("bookclub:details",slug=slug)
    return render(request,'details.html',context)

def create_book_club(request):
    form = BookClubForm
    return render(request, "bookclub.html", {"form": form})
