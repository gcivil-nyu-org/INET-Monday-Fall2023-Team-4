from django.test import TestCase, Client
from user.models import CustomUser
from .models import Notification, TransferOwnershipNotif, BookClubUpdatesNotif
from BookClub.models import BookClub
from libraries.models import Library
from django.urls import reverse


class NotificationModelsTestCase(TestCase):
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
        self.user = CustomUser.objects.create(
            username="testuser",
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
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.user,
        )

    def test_notification_model(self):
        notification = Notification.objects.create(is_read=True, safe_to_delete=False)
        self.assertTrue(isinstance(notification, Notification))
        self.assertTrue(notification.is_read)
        self.assertFalse(notification.safe_to_delete)
        self.assertIsNotNone(notification.date_created)

    def test_transfer_ownership_notif_model(self):
        transfer_notification = TransferOwnershipNotif.objects.create(
            is_read=True,
            safe_to_delete=False,
            original_owner=self.user,
            new_owner=self.member_user,
            book_club=self.book_club,
            status="pending",
        )
        self.assertTrue(isinstance(transfer_notification, Notification))
        self.assertTrue(isinstance(transfer_notification, TransferOwnershipNotif))
        self.assertTrue(transfer_notification.is_read)
        self.assertFalse(transfer_notification.safe_to_delete)
        self.assertIsNotNone(transfer_notification.date_created)
        self.assertEqual(transfer_notification.original_owner, self.user)
        self.assertEqual(transfer_notification.book_club, self.book_club)
        self.assertEqual(transfer_notification.status, "pending")

    def test_book_club_updates_notif_model(self):
        fields_changed = "field1--!!--field2--!!--field3--!!--"
        updates_notification = BookClubUpdatesNotif.objects.create(
            is_read=True,
            safe_to_delete=False,
            receiving_user=self.user,
            book_club=self.book_club,
            fields_changed=fields_changed,
        )
        self.assertTrue(isinstance(updates_notification, Notification))
        self.assertTrue(isinstance(updates_notification, BookClubUpdatesNotif))
        self.assertTrue(updates_notification.is_read)
        self.assertFalse(updates_notification.safe_to_delete)
        self.assertIsNotNone(updates_notification.date_created)
        self.assertEqual(updates_notification.receiving_user, self.user)
        self.assertEqual(updates_notification.book_club, self.book_club)
        self.assertEqual(updates_notification.fields_changed, fields_changed)
        self.assertEqual(
            updates_notification.fields_changed_to_list(),
            ["field1", "field2", "field3"],
        )


class NotificationListViewTestCase(TestCase):
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
            NYU=0,
        )
        self.user = CustomUser.objects.create(
            username="testuser",
            email="admin@email.com",
            first_name="test1first",
            last_name="test1last",
        )
        self.owner_user = CustomUser.objects.create(
            username="owner",
            email="member@nyu.edu",
            first_name="test2first",
            last_name="test2last",
        )
        self.book_club = BookClub.objects.create(
            id=500,
            name="Test Book Club",
            description="This is a test book club",
            currentBook="Sample Book",
            meetingDay="monday",
            meetingOccurence="one",
            libraryId=self.library,
            admin=self.owner_user,
        )
        self.client = Client()

    def test_post_transfer_decline(self):
        self.client.login(username="testuser", password="testpassword")
        transfer_notification = TransferOwnershipNotif.objects.create(
            new_owner=self.user,
            original_owner=self.owner_user,
            book_club=self.book_club,
            status="pending",
        )

        url = reverse("notifications:notifications")
        data = {
            "notif_type": "transfer",
            "status": "Decline",
            "id": str(transfer_notification.id),
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        transfer_notification.refresh_from_db()
        self.assertEqual(transfer_notification.status, "declined")

    def test_post_updates_delete(self):
        self.client.login(username="testuser", password="testpassword")
        updates_notification = BookClubUpdatesNotif.objects.create(
            receiving_user=self.user,
            book_club=self.book_club,
            fields_changed="field1--!!--field2--!!--field3--!!--",
        )

        url = reverse("notifications:notifications")
        data = {
            "notif_type": "updates",
            "id": str(updates_notification.id),
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(BookClubUpdatesNotif.DoesNotExist):
            updates_notification.refresh_from_db()
