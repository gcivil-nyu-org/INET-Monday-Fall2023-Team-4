from django.test import TestCase, RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from django.urls import reverse
from .forms import BookClubForm
from django.http import HttpRequest
from .models import BookClub, PollChoice, VotingPoll
from .views import edit_book_club, book_club_details, create_book_club, getBookInfo
from user.models import CustomUser
from libraries.models import Library
from books.models import Book
import datetime
from django.core import mail


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
        self.client.force_login(self.admin_user)
        response = self.client.get(
            reverse("create-book-club") + "?libraryId=" + str(self.library.id)
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookclub.html")
        self.assertIsInstance(response.context["form"], BookClubForm)

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
        response = self.client.get(reverse("details", args=[self.book_club_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "details.html")

    def test_edit_book_club_view_post(self):
        form_data = {
            "new_admin": self.non_member_user.id,
            "name": "Updated Book Club Name",
            "description": "Updated Description",
            "currentBook": "New Book",
            "currentAuthor": "New Author",
            "currentBookIsbn": 123456789,
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

    def test_edit_book_club_form_save(self):
        form_data = {
            "name": "Updated Book Club Name",
            "description": "Updated Description",
            "currentBook": "New Book",
            "currentAuthor": "New Author",
            "currentBookIsbn": 123456789,
            "meetingDay": "monday",
            "meetingStartTime": datetime.time(18, 0),
            "meetingEndTime": datetime.time(18, 0),
            "meetingOccurence": "one",
            "libraryId": self.library,
            "new_admin": self.admin_user,
        }

        request = HttpRequest()
        request.method = "POST"
        request.user = self.admin_user
        request.POST = form_data

        response = edit_book_club(request, self.book_club_id)

        self.assertEqual(response.status_code, 302)
        # self.assertEqual(
        #     BookClub.objects.get(id=self.book_club_id).name, "Updated Book Club Name"
        # )
        # self.assertEqual(
        #     BookClub.objects.get(id=self.book_club_id).description,
        #     "Updated Description",
        # )
        # self.assertEqual(
        #     BookClub.objects.get(id=self.book_club_id).currentBook, "New Book"
        # )

    def test_non_admin_access_edit_page(self):
        self.client.login(username="non_member_user", password="testpassword")

        url = reverse("edit_book_club", args=[self.book_club_id])
        request = self.factory.get(url)
        request.user = self.non_member_user

        response = edit_book_club(request, book_club_id=self.book_club_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/bookclub/error")


class NYUStatusLogicTests(TestCase):
    def setUp(self):
        self.user_nyu = CustomUser.objects.create(
            username="nyu_user",
            email="nyu_user@nyu.edu",
            first_name="NYU",
            last_name="Tester",
            status="nyu",
        )
        self.user_non_nyu = CustomUser.objects.create(
            username="non_nyu_user",
            email="non_nyu_user@gmail.com",
            first_name="Non-NYU",
            last_name="Tester",
            status="reader",
        )
        self.library_nyu = Library.objects.create(
            id=1,
            branch="NYU Library",
            address="123 Test Unit Drive",
            city="NYC",
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
            NYU="1",
        )
        self.library_non_nyu = Library.objects.create(
            id=2,
            branch="Non-NYU Library",
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
            NYU="0",
        )
        self.nyu_book_club = BookClub.objects.create(
            id=1, name="NYU Book Club", admin=self.user_nyu, libraryId=self.library_nyu
        )
        self.non_nyu_book_club = BookClub.objects.create(
            id=2,
            name="Test Book Club",
            admin=self.user_non_nyu,
            libraryId=self.library_non_nyu,
        )
        self.factory = RequestFactory()

    def test_nyu_user_can_subscribe_to_nyu_club(self):
        self.assertTrue(self.user_nyu.status == "nyu")
        self.assertTrue(self.library_nyu.NYU == "1")

        form_data = {"subscribe": ""}

        request = HttpRequest()
        request.method = "POST"
        request.user = self.user_nyu
        request.POST = form_data

        response = book_club_details(request, self.nyu_book_club.id)
        self.assertEqual(response.status_code, 302)

        self.assertIn(self.user_nyu, self.nyu_book_club.members.all())

    def test_nyu_user_can_subscribe_to_non_nyu_club(self):
        self.assertTrue(self.user_nyu.status == "nyu")
        self.assertTrue(self.library_non_nyu.NYU == "0")

        form_data = {"subscribe": ""}

        request = HttpRequest()
        request.method = "POST"
        request.user = self.user_nyu
        request.POST = form_data

        response = book_club_details(request, self.non_nyu_book_club.id)
        self.assertEqual(response.status_code, 302)

        self.assertIn(self.user_nyu, self.non_nyu_book_club.members.all())

    def test_non_nyu_user_cannot_subscribe_to_nyu_club(self):
        self.assertTrue(self.user_non_nyu.status == "reader")
        self.assertTrue(self.library_nyu.NYU == "1")

        form_data = {"subscribe": ""}

        request = HttpRequest()
        request.method = "POST"
        request.user = self.user_non_nyu
        request.POST = form_data

        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)

        response = book_club_details(request, self.nyu_book_club.id)
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(self.user_non_nyu, self.nyu_book_club.members.all())

    def test_non_nyu_user_can_subscribe_to_non_nyu_club(self):
        self.assertTrue(self.user_non_nyu.status == "reader")
        self.assertTrue(self.library_non_nyu.NYU == "0")

        form_data = {"subscribe": ""}

        request = HttpRequest()
        request.method = "POST"
        request.user = self.user_non_nyu
        request.POST = form_data

        response = book_club_details(request, self.non_nyu_book_club.id)
        self.assertEqual(response.status_code, 302)

        self.assertIn(self.user_non_nyu, self.non_nyu_book_club.members.all())

    def test_user_can_unsubscribe(self):
        self.non_nyu_book_club.members.add(self.user_nyu)
        form_data = {"unsubscribe": ""}

        request = HttpRequest()
        request.method = "POST"
        request.user = self.user_nyu
        request.POST = form_data

        response = book_club_details(request, self.non_nyu_book_club.id)
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(self.user_nyu, self.non_nyu_book_club.members.all())

    def test_create_book_club_nyu_user_nyu_library(self):
        request = self.factory.post("/create/", {"libraryId": self.library_nyu.id})
        request.user = self.user_nyu
        response = create_book_club(request)
        self.assertEqual(response.status_code, 200)
        book_club = BookClub.objects.get(admin=self.user_nyu)
        self.assertEqual(book_club.admin, self.user_nyu)
        self.assertEqual(book_club.libraryId, self.library_nyu)

    def test_create_book_club_non_nyu_user_nyu_library(self):
        request = self.factory.post("/create/", {"libraryId": self.library_nyu.id})
        request.user = self.user_non_nyu
        response = create_book_club(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/bookclub/error")

    def test_create_book_club_nyu_user_non_nyu_library(self):
        request = self.factory.post("/create/", {"libraryId": self.library_non_nyu.id})
        request.user = self.user_nyu
        response = create_book_club(request)
        self.assertEqual(response.status_code, 200)

    def test_create_book_club_non_nyu_user_non_nyu_library(self):
        request = self.factory.post("/create/", {"libraryId": self.library_non_nyu.id})
        request.user = self.user_non_nyu
        response = create_book_club(request)
        self.assertEqual(response.status_code, 200)
        book_club = BookClub.objects.get(admin=self.user_non_nyu)
        self.assertEqual(book_club.admin, self.user_non_nyu)
        self.assertEqual(book_club.libraryId, self.library_non_nyu)


class BookClubDeletionTest(TestCase):
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
        self.delete_url = reverse("delete_book_club")

    def test_delete_book_club_by_admin(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            self.delete_url, {"book_club_id": self.book_club.id}
        )
        with self.assertRaises(BookClub.DoesNotExist):
            BookClub.objects.get(id=self.book_club.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Book Club Deletion Notification")
        recipients = [
            self.admin_user.email,
            self.member_user.email,
        ]  # List all member emails
        self.assertListEqual(mail.outbox[0].to, recipients)
        self.assertRedirects(response, reverse("deletion_confirmation"))

    def test_delete_book_club_by_non_admin(self):
        self.client.force_login(self.member_user)
        response = self.client.post(
            self.delete_url, {"book_club_id": self.book_club.id}
        )
        self.assertTrue(BookClub.objects.filter(id=self.book_club.id).exists())
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/bookclub/error")


class PollChoiceModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.choice = PollChoice.objects.create(name="Choice 1", votes=1)
        self.choice.user_voted.add(self.user)
        self.assertEqual(self.choice.votes, 1)

    def test_remove_user(self):
        self.assertEqual(self.choice.votes, 1)
        self.choice.remove_user(self.user)
        self.assertEqual(self.choice.votes, 0)

    def test_get_votes(self):
        self.assertEqual(self.choice.get_votes(), 1)

    def test_str_method(self):
        self.assertEqual(str(self.choice), "Choice 1")


class VotingPollModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="member",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.choice = PollChoice.objects.create(name="Choice 1", votes=1)
        self.poll = VotingPoll.objects.create(name="Poll 1", poll_set=False)
        self.poll.choices.add(self.choice)
        self.poll.who_voted.add(self.user)
        self.assertEqual(self.choice.votes, 1)

    def test_remove_user_from_poll(self):
        self.assertEqual(self.choice.votes, 1)
        self.poll.remove_user_from_poll(self.user)
        self.choice.remove_user(self.user)
        # self.assertEqual(self.choice.votes, 0)

    def test_did_vote(self):
        self.assertTrue(self.poll.did_vote(self.user))

    def test_get_all_votes(self):
        self.assertEqual(self.poll.get_all_votes(), 1)

    def test_str_method(self):
        self.assertEqual(str(self.poll), "Poll 1")


class VotingFormViewTestCase(TestCase):
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
        self.poll = VotingPoll.objects.create(poll_set=False, name="Test Poll")
        self.choice1 = PollChoice.objects.create(name="Choice 1", votes=0)
        self.choice2 = PollChoice.objects.create(name="Choice 2", votes=0)
        self.choice3 = PollChoice.objects.create(name="Choice 3", votes=0)
        self.poll.choices.add(self.choice1, self.choice2, self.choice3)
        self.book_club.polls = self.poll.id
        self.book_club.save()
        self.client = Client()

    def test_get_voting_form(self):
        url = reverse("voting", args=[str(self.book_club.id)])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "voting.html")
        self.assertIn("previous_form", response.context)
        self.assertIn("who_voted", response.context)
        self.assertIn("choice1", response.context)
        self.assertIn("choice2", response.context)
        self.assertIn("choice3", response.context)

    def test_post_voting_form(self):
        url = reverse("voting", args=[str(self.book_club.id)])
        data = {
            "submit": "submit",
            "book1": "Book 1",
            "book2": "Book 2",
            "book3": "Book 3",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("details", args=[str(self.book_club.id)])
        )

        self.book_club.refresh_from_db()
        self.assertTrue(self.book_club.polls != 0)
        new_poll = VotingPoll.objects.get(id=self.book_club.polls)
        self.assertTrue(new_poll.poll_set)
        self.assertEqual(new_poll.name, "Voting Poll for Test Book Club")

        choices = new_poll.choices.all()
        self.assertEqual(choices[0].name, "Book 1")
        self.assertEqual(choices[1].name, "Book 2")
        self.assertEqual(choices[2].name, "Book 3")


class BookClubDetailsViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="admin",
            email="admin@nyu.edu",
            first_name="Admin",
            last_name="Tester",
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
        self.choice1 = PollChoice.objects.create(name="Choice 1", votes=0)
        self.choice2 = PollChoice.objects.create(name="Choice 2", votes=0)
        self.choice3 = PollChoice.objects.create(name="Choice 3", votes=0)
        self.poll = VotingPoll.objects.create(poll_set=True, name="Test Poll", id=1)
        self.poll.choices.add(self.choice1)
        self.poll.choices.add(self.choice2)
        self.poll.choices.add(self.choice3)
        self.poll.choices.add(self.choice1, self.choice2, self.choice3)
        self.book_club = BookClub.objects.create(
            name="Test Book Club",
            description="This is a test book club",
            currentBook="Sample Book",
            meetingDay="monday",
            meetingStartTime=timezone.now(),
            meetingEndTime=timezone.now(),
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.user,
            polls=self.poll.id,
        )
        self.book_club.polls = self.poll.id
        self.poll.save()
        self.client = Client()

    def test_get_book_club_details(self):
        url = reverse("details", args=[str(self.book_club.id)])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "details.html")
        self.assertIn("bookclub", response.context)
        self.assertIn("member_count", response.context)
        self.assertIn("subscribed", response.context)
        self.assertIn("voting_poll", response.context)
        self.assertIn("choices", response.context)
        self.assertIn("amount_voted", response.context)
        self.assertIn("voted", response.context)
        self.assertIn("is_member", response.context)

    def test_post_subscribe(self):
        self.client.force_login(self.user)
        url = reverse("details", args=[str(self.book_club.id)])
        data = {"subscribe": "subscribe"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("details", args=[str(self.book_club.id)])
        )

        self.book_club.refresh_from_db()
        self.assertTrue(self.user in self.book_club.members.all())

    def test_post_choice1(self):
        self.client.force_login(self.user)
        url = reverse("details", args=[self.book_club.id])
        data = {"choice1": "choice1"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("details", args=[self.book_club.id]))

    def test_post_choice2(self):
        self.client.force_login(self.user)
        url = reverse("details", args=[self.book_club.id])
        data = {"choice2": "choice2"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("details", args=[self.book_club.id]))

    def test_post_choice3(self):
        self.client.force_login(self.user)
        url = reverse("details", args=[self.book_club.id])
        data = {"choice3": "choice3"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("details", args=[self.book_club.id]))


class GetBookInfoTestCase(TestCase):
    def test_create_new_book(self):
        current_book = "New Book"
        current_author = "New Author"
        current_book_isbn = "1234567890"

        self.assertEqual(Book.objects.filter(title=current_book).count(), 0)
        self.assertEqual(Book.objects.filter(isbn=current_book_isbn).count(), 0)

        created_book = getBookInfo(current_book, current_author, current_book_isbn)

        self.assertIsNotNone(created_book)
        self.assertEqual(created_book.title, current_book)
        self.assertEqual(created_book.author, current_author)
        self.assertEqual(created_book.isbn, current_book_isbn)

    def test_existing_book(self):
        existing_book = Book.objects.create(
            title="Existing Book", author="Existing Author", isbn="9876543210"
        )

        current_book = "Existing Book"
        current_author = "Existing Author"
        current_book_isbn = "9876543210"

        self.assertEqual(Book.objects.filter(title=current_book).count(), 1)
        self.assertEqual(Book.objects.filter(isbn=current_book_isbn).count(), 1)

        found_book = getBookInfo(current_book, current_author, current_book_isbn)

        self.assertIsNotNone(found_book)
        self.assertEqual(found_book, existing_book)
