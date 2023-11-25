from django.test import TestCase, RequestFactory
from user.forms import UserRegisterForm, UpdateUserForm, ValidateForm
from django.urls import reverse
from BookClub.models import BookClub
from user.models import CustomUser
from libraries.models import Library
from user.views import user_profile, unsubscribe, mute
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch
from smtplib import SMTPException
from django.test import Client
import datetime


class LoginViewTest(TestCase):
    def setUp(self):
        formdata = {
            "first_name": "test3first",
            "last_name": "test3last",
            "password1": "testP@ssword1",
            "password2": "testP@ssword1",
            "username": "test3",
            "email": "test3@email.com",
        }
        self.testvalidformdata = formdata
        self.testvalidform = UserRegisterForm(data=formdata)

    def test_invalid_credentials(self):
        formdata = {
            "username": "invalid",
            "password": "invalid",
        }
        response = self.client.post(reverse("users:login"), formdata)
        self.assertEqual(response.status_code, 200)

    def test_valid_credentials(self):
        formdata = {
            "username": "test3",
            "password": "testP@ssword1",
        }
        postdata = {"signup": ""}
        postdata.update(self.testvalidformdata)
        response = self.client.post(reverse("users:register"), postdata)
        code = self.client.session.get("verification_code")["code"]
        postdata = {"verify": "", "code": code}
        response = self.client.post(reverse("users:register"), postdata)
        response = self.client.post(reverse("users:login"), formdata)
        self.assertRedirects(response, reverse("users:index"))

    def test_register_email_failure(self):
        with patch("user.views.send_mail") as mocked_send_mail:
            mocked_send_mail.side_effect = SMTPException("Simulated SMTP exception")
            response = self.client.post(reverse("users:register"), {"signup": ""})
            self.assertEqual(response.status_code, 200)


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        formdata = {
            "first_name": "test3first",
            "last_name": "test3last",
            "password1": "testP@ssword1",
            "password2": "testP@ssword1",
            "username": "test3",
            "email": "test3@email.com",
        }
        self.user = CustomUser.objects.create(
            username=formdata["username"],
            email=formdata["email"],
            first_name=formdata["first_name"],
            last_name=formdata["last_name"],
        )
        self.testvalidformdata = formdata
        self.testvalidform = UserRegisterForm(data=formdata)

    def login(self):
        self.client.login(username="test3", password="testP@ssword1")

    def test_profile_page(self):
        response = self.client.get(reverse("users:user_profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_credential_change(self):
        newformdata = self.testvalidformdata.copy()
        newformdata["first_name"] = "newfirstname"
        request = {"user": self.testvalidform["username"], "update": ""}
        request.update(newformdata)
        self.login()
        req = self.factory.post(reverse("users:user_profile"), request)
        req.user = self.user
        req.session = self.client.session
        setattr(req, "session", "session")
        messages = FallbackStorage(req)
        setattr(req, "_messages", messages)
        response = user_profile(req)
        self.assertEqual(response.status_code, 302)

    def test_profile_email_credential_change(self):
        newformdata = self.testvalidformdata.copy()
        newformdata["email"] = "test@email.com"
        request = {"update": ""}
        request.update(newformdata)
        req = self.factory.post(reverse("users:user_profile"), request)
        req.user = self.user
        req.session = self.client.session
        response = user_profile(req)
        self.assertEqual(response.status_code, 200)


class UserViewTest(TestCase):
    def setUp(self):
        formdata = {
            "first_name": "test3first",
            "last_name": "test3last",
            "password1": "testP@ssword1",
            "password2": "testP@ssword1",
            "username": "test3",
            "email": "test3@email.com",
        }
        self.testvalidformdata = formdata
        self.testvalidform = UserRegisterForm(data=formdata)

    def test_register(self):
        response = self.client.get(reverse("users:register"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_forms(self):
        self.assertTrue(self.testvalidform.is_valid())

    def test_post_valid_signup_forms(self):
        postdata = {"signup": ""}
        postdata.update(self.testvalidformdata)
        response = self.client.post(reverse("users:register"), postdata)
        self.assertTrue("verify_code" in response.context)

    def test_post_valid_verify_forms(self):
        postdata = {"signup": ""}
        postdata.update(self.testvalidformdata)
        response = self.client.post(reverse("users:register"), postdata)
        code = self.client.session.get("verification_code")["code"]
        postdata = {"verify": "", "code": code}
        response = self.client.post(reverse("users:register"), postdata)
        self.assertRedirects(response, reverse("users:index"))


class UserFormsTestCase(TestCase):
    def test_user_register_form(self):
        self.user = CustomUser.objects.create(email="existing@email.com")
        formdata = {
            "first_name": "test3first",
            "last_name": "test3last",
            "password1": "testP@ssword1",
            "password2": "testP@ssword1",
            "username": "test3",
            "email": "existing@email.com",
        }
        new_form = UserRegisterForm(formdata)
        self.assertFalse(new_form.is_valid())
        self.assertIn(
            "Email already exists! Please use another email.", new_form.errors["email"]
        )

        formdata["email"] = "invalidemail"
        form = UserRegisterForm(formdata)
        self.assertFalse(form.is_valid())
        self.assertIn("Enter a valid email address.", form.errors["email"])

        formdata["password1"] = "123456"
        form = UserRegisterForm(formdata)
        self.assertFalse(form.is_valid())
        self.assertIn("Password cannot only contain numbers", form.errors["password1"])

        formdata["password1"] = "abcdefg"
        form = UserRegisterForm(formdata)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Password cannot only contain characters", form.errors["password1"]
        )

    def test_update_user_form(self):
        self.user = CustomUser.objects.create(email="existing@update.com")
        formdata = {
            "first_name": "test3first",
            "last_name": "test3last",
            "password1": "testP@ssword1",
            "password2": "testP@ssword1",
            "username": "test3",
            "email": "existing@update.com",
        }
        new_form = UpdateUserForm(formdata)
        self.assertFalse(new_form.is_valid())
        self.assertIn(
            "Email already exists! Please use another email.", new_form.errors["email"]
        )

        formdata["email"] = "invalidemail"
        form = UpdateUserForm(formdata)
        self.assertFalse(form.is_valid())
        self.assertIn("Enter a valid email address.", form.errors["email"])

    def test_validate_form(self):
        data = {
            "code": "special#code",
        }
        form = ValidateForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn("Only alphanumeric characters are allowed.", form.errors["code"])


class SilenceNotificationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create(
            username="TestMute",
            email="TestMute@email.com",
            first_name="Testing",
            last_name="Testing",
        )
        self.library = Library.objects.create(
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
        self.bc = BookClub.objects.create(
            name="Test Book Club",
            description="This is a test book club to mute",
            currentBook="Sample Book",
            meetingDay="monday",
            meetingStartTime=datetime.time(18, 0),
            meetingEndTime=datetime.time(18, 0),
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.user,
        )
        self.bc.members.add(self.user)

    def test_invalid_muting(self):
        response = self.client.get(
            reverse("users:mute", args=[self.bc.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_valid_muting(self):
        request = self.factory.post(
            reverse("users:mute", args=[self.bc.id]),
            {"mute": ""},
        )
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = self.user
        response = mute(request, slug=self.bc.id)
        self.assertEqual(response.status_code, 302)

    def test_valid_unmuting(self):
        request = self.factory.post(
            reverse("users:mute", args=[self.bc.id]),
            {"unmute": ""},
        )
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        request.user = self.user
        response = mute(request, slug=self.bc.id)
        self.assertEqual(response.status_code, 302)


class UnsubscribeTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.book_club = BookClub.objects.create(
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
        self.factory = RequestFactory()

    def test_unsubscribe_view(self):
        user = CustomUser.objects.create(
            id=3,
            username="Tester3",
            email="testers3@nyu.edu",
            first_name="Testing3",
            last_name="Testing3",
        )
        self.book_club.members.add(user.id)
        request = self.factory.post(
            reverse("users:unsubscribe", kwargs={"slug": self.book_club.id})
        )
        request.user = user
        request.session = {}
        messages = FallbackStorage(request)
        request._messages = messages
        response = unsubscribe(request, slug=self.book_club.id)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(user, self.book_club.members.all())
        messages = list(messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Unsubscribe action complete")

    def test_unsubscribe_view_owner_attempt(self):
        request = self.factory.post(
            reverse("users:unsubscribe", kwargs={"slug": self.book_club.id})
        )
        request.user = self.user
        self.book_club.admin = self.user
        self.book_club.save()
        setattr(request, "session", "session")
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = unsubscribe(request, slug=self.book_club.id)
        self.assertEqual(response.status_code, 302)

    def test_unsubscribe_view_invalid_bookclub(self):
        request = self.factory.post(reverse("users:unsubscribe", kwargs={"slug": 999}))
        request.user = self.user
        response = unsubscribe(request, slug=999)
        self.assertEqual(response.status_code, 302)
