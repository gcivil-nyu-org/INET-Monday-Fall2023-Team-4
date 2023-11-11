from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.urls import reverse
from django.http import HttpRequest
from .models import BookClub
from .forms import BookClubEditForm
from .views import edit_book_club
from user.models import CustomUser
from libraries.models import Library
import datetime


class BookClubModelTest(TestCase):
    def setUp(self):
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
        self.admin_user = CustomUser.objects.create(
            username="admin",
            email="admin@email.com",
            first_name="test1first",
            last_name="test1last",
        )
        self.member_user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.book_club = BookClub.objects.create(
            name="Test Book Club",
            description="This is a test book club",
            currentBook="Sample Book",
            meetingDay="monday",
            meetingStartTime=timezone.now(),
            meetingEndTime=timezone.now(),
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.admin_user,
        )
        self.book_club.members.add(self.admin_user, self.member_user)

    def test_book_club_creation(self):
        self.assertEqual(self.book_club.name, "Test Book Club")
        self.assertEqual(self.book_club.description, "This is a test book club")
        self.assertEqual(self.book_club.currentBook, "Sample Book")
        self.assertEqual(self.book_club.meetingDay, "monday")

    def test_book_club_admin(self):
        self.assertEqual(self.book_club.admin, self.admin_user)

    def test_book_club_members(self):
        self.assertIn(self.admin_user, self.book_club.members.all())
        self.assertIn(self.member_user, self.book_club.members.all())
        self.assertEqual(self.book_club.members.count(), 2)

    def test_string_representation(self):
        club = self.book_club
        self.assertEqual(str(club), "Test Book Club")


class BookClubViewsTest(TestCase):
    def setUp(self):
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
        self.admin_user = CustomUser.objects.create(
            username="admin",
            email="admin@email.com",
            first_name="test1first",
            last_name="test1last",
        )
        self.member_user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.non_member_user = CustomUser.objects.create(
            username="non_member",
            email="non_member@yahoo.com",
            first_name="test3first",
            last_name="test3last",
        )
        self.book_club = BookClub.objects.create(
            name="Test Book Club",
            description="This is a test book club",
            currentBook="Sample Book",
            meetingDay="monday",
            meetingStartTime=datetime.time(18, 0),
            meetingEndTime=datetime.time(18, 0),
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.admin_user,
        )
        self.book_club.members.add(self.admin_user, self.member_user)
        self.book_club_id = self.book_club.id
        self.factory = RequestFactory()

    def test_create_book_club_view(self):
        response = self.client.get(reverse("create-book-club"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookclub.html")
        # self.assertIsInstance(response.context["form"], BookClubForm)

    def test_edit_book_club_view(self):
        self.client.login(username="admin", password="adminpassword")

        url = reverse("edit_book_club", args=[self.book_club_id])
        request = self.factory.post(
            url,
            {
                "name": "Updated Book Club Name",
                "description": "Updated Description",
            },
        )
        request.user = self.admin_user
        response = edit_book_club(request, book_club_id=self.book_club_id)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_book_club_detail_view(self):
        response = self.client.get(
            reverse("book_club_detail", args=[self.book_club_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookclub_detail.html")
        self.assertEqual(response.context["book_club"], self.book_club)

    def test_edit_book_club_view_post(self):
        form_data = {
            "admin": self.non_member_user.id,
            "name": "Updated Book Club Name",
            "description": "Updated Description",
            "currentBook": "New Book",
            "meetingDay": "monday",
            "meetingStartTime": datetime.time(18, 0),
            "meetingEndTime": datetime.time(18, 0),
            "meetingOccurence": "one",
            "libraryId": self.library,
        }

        request = HttpRequest()
        request.method = "POST"
        request.user = self.admin_user
        request.POST = form_data

        response = edit_book_club(request, self.book_club_id)

        updated_book_club = BookClub.objects.get(id=self.book_club_id)

        self.assertEqual(updated_book_club.admin, self.non_member_user)
        self.assertIn(self.non_member_user, updated_book_club.members.all())
        self.assertEqual(response.status_code, 302)

    def test_edit_book_club_form_save(self):
        form_data = {
            "admin": self.non_member_user.id,
            "name": "Updated Book Club Name",
            "description": "Updated Description",
            "currentBook": "New Book",
            "meetingDay": "monday",
            "meetingStartTime": datetime.time(18, 0),
            "meetingEndTime": datetime.time(18, 0),
            "meetingOccurence": "one",
            "libraryId": self.library,
        }

        request = HttpRequest()
        request.method = "POST"
        request.user = self.admin_user
        request.POST = form_data

        response = edit_book_club(request, self.book_club_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            BookClub.objects.get(id=self.book_club_id).name, "Updated Book Club Name"
        )
        self.assertEqual(
            BookClub.objects.get(id=self.book_club_id).description,
            "Updated Description",
        )
        self.assertEqual(
            BookClub.objects.get(id=self.book_club_id).currentBook, "New Book"
        )

    def test_non_admin_access_edit_page(self):
        self.client.login(username="non_member_user", password="testpassword")

        url = reverse("edit_book_club", args=[self.book_club_id])
        request = self.factory.get(url)
        request.user = self.non_member_user

        response = edit_book_club(request, book_club_id=self.book_club_id)
        self.assertEqual(response.status_code, 403)
