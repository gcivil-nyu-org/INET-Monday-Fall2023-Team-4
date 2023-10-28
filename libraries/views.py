from django.http import HttpResponse
from django.template import loader

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from libraries.models import Library

# Create your views here.


def index(request):
    template = loader.get_template("libraries/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


class LibraryDetailView(DetailView):
    model = Library


class LibraryListView(ListView):
    model = Library

    paginate_by = 10

    # def get_context_data(self, **kwargs):
    #     context = super(LibraryListView, self).get_context_data(**kwargs)
    #     context["random data"] = "placeholder"
    #     return context
