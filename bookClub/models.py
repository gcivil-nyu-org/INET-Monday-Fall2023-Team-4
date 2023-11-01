from django.db import models
from user.models import CustomUser
from libraries.models import Library

# Create your models here.
class BookClub(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    currentBook = models.CharField(max_length=150)
    meetingSchedule = models.TextField()
    libraryId = models.ForeignKey(Library, on_delete=models.CASCADE)
    adminId = models.SmallIntegerField()
    members = models.ManyToManyField(CustomUser, related_name="book_clubs")

