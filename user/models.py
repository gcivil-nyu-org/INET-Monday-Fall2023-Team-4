import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from Notifications.models import Notification
from django.db.models import Q


class CustomUser(AbstractUser):
    STATUS = (
        ("reader", "Reader"),
        ("librarian", "Librarian"),
        ("nyu", "NYU Associated"),
    )

    username = models.CharField(max_length=50, blank=True, null=True, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True, unique=False)
    last_name = models.CharField(max_length=50, blank=True, null=True, unique=False)
    status = models.CharField(max_length=100, choices=STATUS, default="reader")

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [
        "email",
    ]

    def get_unread_notifications(self):
        unread_notifications = Notification.objects.filter(
            Q(
                transferownershipnotif__new_owner=self.id,
                transferownershipnotif__status="pending",
                is_read=False,
            )
            | Q(
                transferownershipnotif__original_owner=self.id,
                transferownershipnotif__status="declined",
                is_read=False,
            )
            | Q(bookclubupdatesnotif__receiving_user=self.id, is_read=False)
        ).count()

        return unread_notifications

    def get_user_status(email):
        domain = re.search(r"@[\w.]+", email).group()
        if domain == "@nyu.edu":
            return "nyu"
        else:
            return "reader"

    def save(self, *args, **kwargs):
        self.status = CustomUser.get_user_status(self.email)
        super(CustomUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
