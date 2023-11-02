from django.http import HttpResponse
from django.template import loader

from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.db.models import Q
from libraries.models import Library


def index(request):
    template = loader.get_template("libraries/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


class LibraryDetailView(DetailView):
    model = Library


class LibraryListView(ListView):
    model = Library
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("search")

        if query:
            object_list = Library.objects.filter(
                Q(branch__icontains=query) | Q(postcode__icontains=query)
            )
        else:
            object_list = Library.objects.all()

        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_value"] = self.request.GET.get("search", "")
        return context
