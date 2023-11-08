from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .forms import BookClubEditForm
from .models import BookClub
from user.models import CustomUser
from libraries.models import Library


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
        self.book_club_id = self.book_club.id

    def test_create_book_club_view(self):
        response = self.client.get(reverse("create-book-club"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookclub.html")
        # self.assertIsInstance(response.context["form"], BookClubForm)

    def test_edit_book_club_view(self):
        response = self.client.post(
            reverse("edit_book_club", args=[self.book_club_id]),
            {
                "name": "Updated Book Club Name",
                "description": "Updated Description",
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("edit_book_club", args=[self.book_club_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookclub_edit.html")
        self.assertIsInstance(response.context["form"], BookClubEditForm)
        self.assertEqual(response.context["book_club"], self.book_club)

    def test_book_club_detail_view(self):
        response = self.client.get(
            reverse("book_club_detail", args=[self.book_club_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookclub_detail.html")
        self.assertEqual(response.context["book_club"], self.book_club)
