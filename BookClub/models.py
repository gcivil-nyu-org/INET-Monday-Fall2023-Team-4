from django.db import models
from user.models import CustomUser
from libraries.models import Library
import datetime


class BookClub(models.Model):
    DAYS_OF_THE_WEEK = [
        ("monday", "Monday"),
        ("tuesday", "Tuesday"),
        ("wednesday", "Wednesday"),
        ("thursday", "Thursday"),
        ("friday", "Friday"),
        ("saturday", "Saturday"),
        ("sunday", "Sunday"),
    ]
    OCCURENCE_CHOICES = [
        ("one", "One-Time"),
        ("weekly", "Weekly"),
        ("bi-weekly", "Bi-weekly"),
        ("monthly", "Monthly"),
    ]
    name = models.CharField(max_length=150)
    description = models.TextField()
    currentBook = models.CharField(max_length=150)
    meetingDay = models.CharField(
        choices=DAYS_OF_THE_WEEK,
        max_length=150,
        null=True,  # Allows the field to be null
        blank=True,
    )  # drop down choice in forms
    meetingStartTime = models.TimeField(default=datetime.time(17, 0))
    meetingEndTime = models.TimeField(default=datetime.time(18, 0))
    meetingOccurence = models.CharField(
        choices=OCCURENCE_CHOICES,
        max_length=150,
        null=True,  # Allows the field to be null
        blank=True,
    )  # drop down choice in forms
    libraryId = models.ForeignKey(
        Library, on_delete=models.CASCADE, related_name="book_clubs"
    )
    admin = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="book_club_admin"
    )
    members = models.ManyToManyField(CustomUser, related_name="book_clubs")

    def __str__(self):
        return self.name
