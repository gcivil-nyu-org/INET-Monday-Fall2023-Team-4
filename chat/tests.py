from django.test import TestCase, Client
from django.urls import reverse
from user.models import CustomUser


class ChatViewsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(
            username="nyu_user",
            email="nyu_user@nyu.edu",
            first_name="NYU",
            last_name="Tester",
            status="nyu",
        )
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse("chat:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/index.html")

    def test_room_view(self):
        self.client.login(username="nyu_user", password="testpassword")

        room_name = "testroom"
        response = self.client.get(reverse("chat:room", args=[room_name]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/room.html")
        self.assertContains(response, room_name)

    def test_name_view(self):
        self.client.login(username="nyu_user", password="testpassword")

        room_name = "testroom"
        response = self.client.get(reverse("chat:name", args=[room_name]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "chat/name.html")
