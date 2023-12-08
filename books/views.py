from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.http import HttpResponseBadRequest
from .models import Book, Rating
from .utils import get_book_cover
from django.contrib import messages
from django.http import HttpResponseRedirect


class BookDetailView(View):
    template_name = "book_rating.html"

    def get(self, request, pk):
        book = Book.objects.get(pk=pk)
        book_cover = get_book_cover(book)
        ratings = Rating.objects.filter(book=book)
        average = book.average_rating
        context = {
            "book": book,
            "ratings": ratings,
            "book_cover": book_cover,
            "average_rating": average,
        }
        return render(request, self.template_name, context)


def rate_book(request, pk):
    if request.method == "POST":
        book = Book.objects.get(pk=pk)
        rating_value = request.POST.get("rating")
        if not rating_value:
            messages.error(request, "You must select a star rating.")
            return HttpResponseRedirect(
                request.META.get("HTTP_REFERER", reverse("book_detail", args=[pk]))
            )

        if rating_value is not None:
            try:
                rating_value = int(rating_value)
                if 1 <= rating_value <= 5:
                    Rating.objects.create(
                        user=request.user, book=book, value=rating_value
                    )
                else:
                    return HttpResponseBadRequest("Invalid rating value")
            except ValueError:
                return HttpResponseBadRequest("Invalid rating value")

        return redirect(reverse("book_detail", args=[pk]))
    else:
        return HttpResponseBadRequest("Invalid request method")
