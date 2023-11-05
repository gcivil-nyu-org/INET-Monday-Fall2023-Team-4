from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.urls import reverse

from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.db.models import Q
from libraries.models import Library
from BookClub.models import BookClub
from Subscription.models import Subscription
from Subscription.forms import JoinClubForm

from datetime import date


def index(request):
    template = loader.get_template("libraries/index.html")
    context = {}
    return HttpResponse(template.render(context, request))


class LibraryDetailView(DetailView):
    model = Library
    template_name = "libraries/library_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book_clubs"] = BookClub.objects.filter(libraryId=self.object.id)
        subs = Subscription.objects.filter(user_id=self.request.user.id)
        bc_pk_list = list(set(sub.book_club_id for sub in subs))
        context["user_clubs"] = BookClub.objects.filter(pk__in=bc_pk_list)
        context["form"] = JoinClubForm()

        return context


class JoinClubFormView(SingleObjectMixin, FormView):
    template_name = "libraries/library_detail.html"
    form_class = JoinClubForm
    model = Library
    success_url = "#"

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        context = {}
        context["book_clubs"] = BookClub.objects.filter(libraryId=self.object.id)
        return reverse("libraries:library-detail", kwargs={"pk": self.object.pk})


class LibraryView(View):
    def get(self, request, *args, **kwargs):
        view = LibraryDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = JoinClubFormView.as_view()
        form = JoinClubForm(request.POST)
        if form.is_valid():
            if "unjoin" in request.POST:
                sub = Subscription.objects.filter(
                    user_id=request.user.id,
                    book_club_id=int(request.POST["bookclub_id"][0]),
                )
                sub.delete()
            else:
                new_sub = Subscription(
                    user_id=request.user.id,
                    book_club_id=int(request.POST["bookclub_id"][0]),
                    date_joined=date.today(),
                )
                new_sub.save()
        return view(request, *args, **kwargs)


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
