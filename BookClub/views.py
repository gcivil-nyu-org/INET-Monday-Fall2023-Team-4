from django.shortcuts import render
from .forms import BookClubForm
from django.conf import settings as conf_settings
from .models import BookClub
from libraries.models import Library
from django.contrib import messages


def book_club_details(request,slug):
    bc = BookClub.objects.get(id=slug)
    context = {
        'key' :conf_settings.GOOGLE_API_KEY,
		'bookclub': bc,
		'member_count': bc.members.all().count(),
		'lat' : 40.660152,
		'lng' : -73.739488
    }
    if request.method == "POST":
        if 'subscribe' in request.POST:
            if (not bc.libraryId.NYU) or (bc.libraryId.NYU and request.user.status == 'nyu'):
                bc.members.add(request.user)
            else:
                messages.error(
                request,
                "You must be a NYU student to subscribe to this book club"
            )
	
    return render(request,'details.html',context)

def create_book_club(request):
    form = BookClubForm
    return render(request, "bookclub.html", {"form": form})
