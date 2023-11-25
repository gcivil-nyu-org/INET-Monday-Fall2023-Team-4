import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


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
    
class TransferOwnershipRequest(models.Model):
    original_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="old_admin")
    new_owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="new_admin")
    book_club = models.ForeignKey('BookClub.BookClub', on_delete=models.CASCADE, related_name="book_club_in_limbo")
    status_types = ['accepted', 'pending', 'declined']
    status = models.CharField(status_types, max_length=30)
    date_created = models.DateField("date created")
    
    class Meta:
        ordering = ["date_created"]
