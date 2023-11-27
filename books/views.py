from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.http import HttpResponseBadRequest
from .models import Book, Rating

class BookListView(View):
    template_name = 'book_list.html'

    def get(self, request):
        books = Book.objects.all()
        context = {'books': books}
        return render(request, self.template_name, context)

class BookDetailView(View):
    template_name = 'book_rating.html'

    def get(self, request, pk):
        book = Book.objects.get(pk=pk)
        ratings = Rating.objects.filter(book=book)
        context = {'book': book, 'ratings': ratings}
        return render(request, self.template_name, context)

def rate_book(request, pk):
    if request.method == 'POST':
        book = Book.objects.get(pk=pk)
        rating_value = request.POST.get('value')

        try:
            rating_value = int(rating_value)
            if 1 <= rating_value <= 5:
                Rating.objects.create(book=book, value=rating_value)
            else:
                return HttpResponseBadRequest("Invalid rating value")
        except ValueError:
            return HttpResponseBadRequest("Invalid rating value")

        return redirect(reverse('book_detail', args=[pk]))
    else:
        return HttpResponseBadRequest("Invalid request method")