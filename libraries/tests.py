from django.test import TestCase, RequestFactory
from django.template.loader import get_template
from django.contrib.auth.models import AnonymousUser
from django.test import Client
from django.urls import reverse
from django.http import HttpRequest

from BookClub.models import BookClub
from user.models import CustomUser
from libraries.models import Library
from libraries.views import (
    index,
    LibraryListView,
    LibraryView,
    JoinClubFormView,
    LibraryDetailView,
)

import datetime

c = Client()


class IndexViewTest(TestCase):
    def test_index_view(self):
        factory = RequestFactory()
        request = factory.get("/")
        response = index(request)
        self.assertEqual(response.status_code, 200)
        expected_template = get_template("libraries/index.html")
        self.assertEqual(response.content, expected_template.render({}).encode())


class LibrariesTestCase(TestCase):
    def setUp(self):
        Library.objects.create(
            id=1,
            branch="Library Test Case Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=1,
        )
        Library.objects.create(
            id=2,
            branch="Library Unit Test Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=0,
        )

    def test_library_ordering(self):
        ordering = Library._meta.ordering
        self.assertEquals(ordering[0], "branch")

    def test_library_information(self):
        branch1 = Library.objects.get(id=1)
        branch2 = Library.objects.get(id=2)
        self.assertEqual(getattr(branch1, "branch"), "Library Test Case Branch")
        self.assertTrue(getattr(branch2, "branch"), "Library Unit Test Branch")

    def test_string_representation(self):
        branch1 = Library.objects.get(id=1)
        self.assertEqual(str(branch1), "Library Test Case Branch")

    def test_get_today_hours(self):
        self.monday = "9:00 AM - 6:00 PM"
        self.tuesday = "9:00 AM - 6:00 PM"
        self.wednesday = "9:00 AM - 6:00 PM"
        self.thursday = "9:00 AM - 6:00 PM"
        self.friday = "9:00 AM - 6:00 PM"
        self.saturday = "9:00 AM - 6:00 PM"
        self.sunday = "9:00 AM - 6:00 PM"

        expected_hours = "9:00 AM - 6:00 PM"
        self.assertEqual(Library.get_today_hours(self), expected_hours)


class TestLibraryViews(TestCase):
    def setUp(self):
        self.library = Library.objects.create(
            branch="Test Library",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=0,
        )

    def test_index_view(self):
        request = HttpRequest()
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_library_list_view(self):
        response = self.client.get(reverse("libraries:library-list"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["object_list"],
            Library.objects.all(),
            transform=lambda x: x,
        )


class TestLibraryListView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.library1 = Library.objects.create(
            id=1,
            branch="Test Case Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=1,
        )
        self.library2 = Library.objects.create(
            id=2,
            branch="Unit Test Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=0,
        )

    def test_search_with_existing_data(self):
        request = self.factory.get(
            reverse("libraries:library-list"), data={"search": "Test Case Branch"}
        )
        response = LibraryListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 1)
        self.assertIn(self.library1, response.context_data["object_list"])

    def test_search_with_nonexistent_data(self):
        request = self.factory.get(
            reverse("libraries:library-list"), data={"search": "Nonexistent Library"}
        )
        response = LibraryListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data["object_list"]), 0)

    def test_context_search_value(self):
        request = self.factory.get(
            reverse("libraries:library-list"), data={"search": "Branch"}
        )
        response = LibraryListView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["search_value"], "Branch")


class LibraryDetailViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.library = Library.objects.create(
            id=1,
            branch="Library Test Case Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=1,
        )
        self.bookclub = BookClub.objects.create(
            name="Test Book Club",
            description="This is a test book club",
            currentBook="Sample Book",
            meetingDay="monday",
            meetingStartTime=datetime.time(18, 0),
            meetingEndTime=datetime.time(18, 0),
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.user,
        )
        self.library_detail_view = LibraryDetailView()
        self.library_detail_view.object = self.bookclub

    def test_get_context_data(self):
        user_id = 1
        request = type("Request", (), {"user": type("User", (), {"id": user_id})})()

        self.library_detail_view.request = request

        context = self.library_detail_view.get_context_data()

        book_clubs = list(
            BookClub.objects.filter(libraryId=self.library_detail_view.object.id)
        )
        bookclubs_ids = BookClub.members.through.objects.filter(customuser_id=user_id)
        bc_pk_list = [bc.bookclub_id for bc in bookclubs_ids]
        user_clubs = list(BookClub.objects.filter(pk__in=bc_pk_list))

        self.assertEqual(list(context["book_clubs"]), book_clubs)
        self.assertEqual(list(context["user_clubs"]), user_clubs)
        self.assertIsNotNone(context["form"])


class JoinClubFormViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.library = Library.objects.create(
            id=1,
            branch="Library Test Case Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=1,
        )
        self.factory = RequestFactory()
        self.join_club_form_view = JoinClubFormView()
        self.join_club_form_view.object = self.library

    def test_post_unauthenticated_user(self):
        request = self.factory.post("/libraries/")
        request.user = AnonymousUser()

        self.join_club_form_view.request = request
        response = self.join_club_form_view.post(request)

        self.assertEqual(response.status_code, 403)

    def test_get_success_url(self):
        request = self.factory.get("/libraries/")
        request.user = self.user

        self.join_club_form_view.request = request
        self.join_club_form_view.object = self.library

        url = self.join_club_form_view.get_success_url()

        expected_url = reverse(
            "libraries:library-detail", kwargs={"pk": self.library.pk}
        )

        self.assertEqual(url, expected_url)


class LibraryViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="Tester",
            email="testers@nyu.edu",
            first_name="Testing",
            last_name="Testing",
        )
        self.library = Library.objects.create(
            id=1,
            branch="Library Test Case Branch",
            address="123 Test Unit Drive",
            city="Coveralls",
            postcode="65432",
            phone="(123)456-7890",
            monday="9:00AM - 5:00PM",
            tuesday="9:00AM - 5:00PM",
            wednesday="9:00AM - 5:00PM",
            thursday="9:00AM - 5:00PM",
            friday="9:00AM - 5:00PM",
            saturday="9:00AM - 5:00PM",
            sunday="9:00AM - 5:00PM",
            latitude=0.0,
            longitude=0.0,
            link="https://github.com/gcivil-nyu-org/",
            NYU=1,
        )
        self.client = Client()
        self.library_view = LibraryView()

    def test_get_method(self):
        response = self.client.get("/libraries/1")
        self.assertEqual(response.status_code, 200)

    def test_post_method_unauthenticated(self):
        request = HttpRequest()
        request.method = "POST"
        request.user = AnonymousUser()

        response = self.library_view.post(request)

        self.assertEqual(response.status_code, 403)
