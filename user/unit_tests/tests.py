from django.test import TestCase
from user.models import CustomUser

# Create your tests here.


class CustomUserTest(TestCase):
    def setUp(self):
        CustomUser.objects.create(
            username="test",
            email="test@email.com",
            first_name="test1first",
            last_name="test1last",
        )
        CustomUser.objects.create(
            username="test2",
            email="test@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )

    def test_get_status(self):
        test1 = CustomUser.objects.get(email="test@email.com")
        test2 = CustomUser.objects.get(email="test@nyu.edu")
        self.assertEqual(CustomUser.get_user_status(test1.email), "reader")
        self.assertEqual(CustomUser.get_user_status(test2.email), "nyu")

    def test_return_str(self):
        test1 = CustomUser.objects.get(email="test@email.com")
        self.assertEqual(test1.username, "test")

    def test_string_representation(self):
        test2 = CustomUser.objects.get(email="test@nyu.edu")
        self.assertEqual(str(test2), "test2")
