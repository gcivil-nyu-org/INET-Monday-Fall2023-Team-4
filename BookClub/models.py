from django.db import models
from user.models import CustomUser
from libraries.models import Library
import datetime


class PollChoice(models.Model):
    name = models.CharField(max_length=200)
    votes = models.PositiveSmallIntegerField()
    user_voted = models.ManyToManyField(CustomUser)

    def remove_user(self, customusr):
        if customusr in self.user_voted.all():
            self.user_voted.remove(customusr)
            self.votes -= 1
            self.save()

    def get_votes(self):
        return self.votes

    def __str__(self):
        return self.name


class VotingPoll(models.Model):
    poll_set = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    choices = models.ManyToManyField(PollChoice)
    who_voted = models.ManyToManyField(CustomUser)

    def remove_user_from_poll(self, customusr):
        for choice in self.choices.all():
            choice.remove_user(customusr)

    def did_vote(self, customusr):
        if customusr in self.who_voted.all():
            return True
        return False

    def get_all_votes(self):
        votes = 0
        for choice in self.choices.all():
            votes += choice.get_votes()
        return votes

    def __str__(self):
        return self.name


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
    currentAuthor = models.CharField(max_length=255, blank=True)
    currentBookIsbn = models.BigIntegerField(null=True)
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
    silenceNotification = models.ManyToManyField(
        CustomUser, related_name="silence_notifications"
    )
    polls = models.IntegerField(default=0)

    def __str__(self):
        return self.name
