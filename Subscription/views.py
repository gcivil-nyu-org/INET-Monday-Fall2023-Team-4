from django.shortcuts import render
from BookClub.models import BookClub
from user.models import CustomUser
from Subscription.models import Subscription

from datetime import date


# Create your views here.
def toggle_club_join(request, user_pk, bookclub_pk):
    sub = Subscription.objects.filter(user_id=user_pk, book_club_id=bookclub_pk)
    if sub.exists():
        target_sub = sub[0]
        target_sub.delete()
    else:
        new_sub = Subscription(
            user_id=user_pk, book_club_id=bookclub_pk, date_joined=date.today()
        )
        new_sub.save()

    context = {}
    context["user_pk"] = user_pk
    context["bookclub_pk"] = bookclub_pk

    return render(request, "library_detail.html", context=context)
