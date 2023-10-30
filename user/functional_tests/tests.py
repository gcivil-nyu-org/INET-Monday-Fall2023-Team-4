from django.test import TestCase, RequestFactory
from user.forms import UserRegisterForm
from django.urls import reverse
from user.models import CustomUser
from user.views import user_profile
from django.contrib.messages.storage.fallback import FallbackStorage


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
        msgs = list(response.context["messages"])
        self.assertEqual(str(msgs[0]), "Account does not exist. Please sign up.")

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
