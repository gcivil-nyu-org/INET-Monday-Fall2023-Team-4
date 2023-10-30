from django.test import TestCase
from django.template.loader import get_template
from django.test import Client
from django.test import RequestFactory

from libraries.models import Library
from libraries.views import index

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
            link="https://github.com/gcivil-nyu-org/INET-Monday-Fall2023-Team-4",
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
            link="https://github.com/gcivil-nyu-org/INET-Monday-Fall2023-Team-4",
            NYU=0,
        )

    def test_library_ordering(self):
        ordering = Library._meta.ordering
        self.assertEquals(ordering[0], "-branch")

    def test_library_information(self):
        branch1 = Library.objects.get(id=1)
        branch2 = Library.objects.get(id=2)
        self.assertEqual(getattr(branch1, "branch"), "Library Test Case Branch")
        self.assertTrue(getattr(branch2, "branch"), "Library Unit Test Branch")

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
