from django.db import models
from datetime import datetime
from django.urls import reverse


class Library(models.Model):
    id = models.AutoField(primary_key=True)
    branch = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    monday = models.CharField(max_length=100, null=True, blank=True)
    tuesday = models.CharField(max_length=100, null=True, blank=True)
    wednesday = models.CharField(max_length=100, null=True, blank=True)
    thursday = models.CharField(max_length=100, null=True, blank=True)
    friday = models.CharField(max_length=100, null=True, blank=True)
    saturday = models.CharField(max_length=100, null=True, blank=True)
    sunday = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6)
    longitude = models.DecimalField(max_digits=10, decimal_places=6)
    link = models.URLField(max_length=1000, null=True, blank=True)
    NYU = models.CharField(max_length=255)

    class Meta:
        ordering = ["branch"]
        db_table = "library"

    def __str__(self):
        return self.branch

    def get_today_hours(self):
        days_in_week = [
            self.monday,
            self.tuesday,
            self.wednesday,
            self.thursday,
            self.friday,
            self.saturday,
            self.sunday,
        ]

        curr_time = datetime.now()
        weekday = curr_time.weekday()
        return days_in_week[weekday]

    def get_absolute_url(self):
        return reverse("libraries:library-detail", kwargs={"pk": self.pk})
