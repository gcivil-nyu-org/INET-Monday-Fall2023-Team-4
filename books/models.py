from django.db import models
from django.db.models import Avg
from user.models import CustomUser


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    isbn = models.BigIntegerField(null=True)

    def average_rating(self) -> float:
        return (
            Rating.objects.filter(book=self).aggregate(Avg("value"))["value__avg"] or 0
        )

    def __str__(self):
        return self.title


class Rating(models.Model):
    STAR_CHOICES = [(i, i) for i in range(1, 6)]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    value = models.IntegerField(choices=STAR_CHOICES, default=0)

    def __str__(self):
        return f"{self.book.title} - {self.value} stars"
