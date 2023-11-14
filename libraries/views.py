from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.contrib import messages

from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import ListView
from django.db.models import Q
from libraries.models import Library
from BookClub.models import BookClub
from BookClub.views import checkIfAllowedToSubscribe
from django.conf import settings as conf_settings
from django.core.exceptions import ObjectDoesNotExist

from .forms import JoinClubForm


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
        bookclubs_ids = BookClub.members.through.objects.filter(
            customuser_id=self.request.user.id
        )
        bc_pk_list = [bc.bookclub_id for bc in bookclubs_ids]
        context["user_clubs"] = BookClub.objects.filter(pk__in=bc_pk_list)
        context["form"] = JoinClubForm()
        context["key"] = conf_settings.GOOGLE_API_KEY

        return context


class JoinClubFormView(SingleObjectMixin, FormView):
    template_name = "libraries/library_detail.html"
    form_class = JoinClubForm
    model = Library
    success_url = "#"

    def post(self, request, *args, **kwargs):
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
            if int(request.POST["user_id"]) == -1:
                messages.error(
                    request,
                    "Please login/ sign up to subscribe to a bookclub!",
                )
            else:
                try:
                    bc = BookClub.objects.get(id=request.POST["bookclub_id"])
                    if "unjoin" in request.POST:
                        if bc.admin == request.user:
                            messages.error(
                                request,
                                "Owner cannot unsubscribe, please reassign ownership first",
                            )
                        else:
                            bc.members.remove(request.user)
                    else:
                        checkIfAllowedToSubscribe(bc, request)
                except ObjectDoesNotExist:
                    messages.error(
                        request,
                        "Something went wrong, please try again.",
                    )
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
